import re
from collections import Counter
from math import isfinite

KICAD_BOARD_FORMAT_VERSION = 20240108
KICAD_GENERATOR = "photonx_eda_pcb"
KICAD_DEFAULT_BOARD_THICKNESS_MM = 1.6
KICAD_DEFAULT_PAD_TO_MASK_CLEARANCE_MM = 0.0
KICAD_DEFAULT_PAPER = "A4"


def kicad_duplicate_object_ids(board):
    objects = [
        *board.tracks,
        *board.pads,
        *board.drills,
        *board.outline,
        *getattr(board, "slots", ()),
        *getattr(board, "regions", ()),
        *getattr(board, "routes", ()),
    ]
    counts = Counter(obj.id for obj in objects)
    return tuple(
        sorted(
            (
                object_id
                for object_id, count in counts.items()
                if count > 1
            ),
            key=str,
        )
    )


def kicad_net_export_rows(board):
    counts = Counter(net.id for net in board.nets)
    duplicate_ids = {
        net_id
        for net_id, count in counts.items()
        if count > 1
    }
    rows = []
    for net in board.nets:
        if net.id in duplicate_ids:
            continue
        rows.append(
            {
                "id": net.id,
                "code": len(rows) + 1,
                "name": str(net.label or net.id),
            }
        )
    return tuple(rows), tuple(sorted(duplicate_ids, key=str))
from photonx_eda_pcb.mechanical_features.measure import slot_geometry_descriptor
_INNER_COPPER_LAYER_RE=re.compile(r"^In([1-9]|[12][0-9]|30)\.Cu$")


def inner_copper_layers(board):
    observed={
        str(getattr(obj,"layer",""))
        for obj in [*board.tracks,*board.pads,*getattr(board,"regions",())]
    }
    indices=[]
    for name in observed:
        match=_INNER_COPPER_LAYER_RE.fullmatch(name)
        if match:
            indices.append(int(match.group(1)))
    highest=max(indices,default=0)
    return tuple((index,f"In{index}.Cu") for index in range(1,highest+1))


def declared_copper_layer_names(board):
    return {"F.Cu","B.Cu"} | {name for _,name in inner_copper_layers(board)}


def kicad_board_layer_specs(board):
    return (
        {"id":0,"name":"F.Cu","type":"signal","suffix":None},
        *(
            {"id":index,"name":name,"type":"signal","suffix":None}
            for index,name in inner_copper_layers(board)
        ),
        {"id":31,"name":"B.Cu","type":"signal","suffix":None},
        {"id":36,"name":"B.SilkS","type":"user","suffix":"b.silkscreen"},
        {"id":37,"name":"F.SilkS","type":"user","suffix":"f.silkscreen"},
        {"id":44,"name":"Edge.Cuts","type":"user","suffix":None},
    )


def kicad_board_layer_rows(board):
    return [
        {"id":row["id"],"name":row["name"],"type":row["type"]}
        for row in kicad_board_layer_specs(board)
    ]


def pad_shape_supported(shape):
    return str(shape or "").upper() in {"C","R","O"}


def pad_export_status(board,pad):
    try:
        cx = float(pad.center.x)
        cy = float(pad.center.y)
    except (TypeError, ValueError):
        return "skip-invalid-coordinate"
    if not all(isfinite(value) for value in (cx, cy)):
        return "skip-invalid-coordinate"

    try:
        size_x = float(pad.size_x)
        size_y = float(pad.size_y)
    except (TypeError, ValueError):
        return "skip-invalid-size"
    if (
        not isfinite(size_x)
        or not isfinite(size_y)
        or size_x <= 0
        or size_y <= 0
    ):
        return "skip-invalid-size"

    try:
        angle = float(
            getattr(
                pad,
                "rotation_deg",
                getattr(pad, "rotation", 0.0),
            )
            or 0.0
        )
    except (TypeError, ValueError):
        return "skip-invalid-rotation"
    if not isfinite(angle):
        return "skip-invalid-rotation"

    if str(pad.layer) not in declared_copper_layer_names(board):
        return "skip-layer"
    if not pad_shape_supported(pad.shape):
        return "skip-shape"
    if pad.drill is not None:
        return "skip-drill-padstack"
    return "export"


def pad_shape_name(shape):
    s=str(shape or "").upper()
    if s=="C":return "circle"
    if s=="O":return "oval"
    if s=="R":return "rect"
    return "rect"
def pad_export_descriptor(pad):
    layer=str(pad.layer)
    ref_layer="B.SilkS" if layer=="B.Cu" else "F.SilkS"
    drill=float(pad.drill) if pad.drill else None
    if drill is not None:
        layers=("*.Cu","*.Mask")
        warning=None
        kind="thru_hole"
    elif layer=="F.Cu":
        layers=("F.Cu","F.Paste","F.Mask")
        warning=None
        kind="smd"
    elif layer=="B.Cu":
        layers=("B.Cu","B.Paste","B.Mask")
        warning=None
        kind="smd"
    else:
        layers=(layer,)
        warning="SMD pad is on a non-surface copper layer; paste/mask layers were not invented"
        kind="smd"
    angle=float(getattr(pad,"rotation_deg",getattr(pad,"rotation",0.0)) or 0.0)
    return {
        "footprint_layer":layer,
        "number":"1",
        "kind":kind,
        "shape":pad_shape_name(pad.shape),
        "pad_at":(0.0,0.0),
        "pad_angle":angle,
        "size":(float(pad.size_x),float(pad.size_y)),
        "drill_shape":"round" if drill is not None else None,
        "drill_size":(drill,drill) if drill is not None else None,
        "drill_offset":(0.0,0.0),
        "layers":layers,
    },ref_layer,warning

_X2_REFDES_EVIDENCE = "gerber_x2_component_refdes"
_X2_PIN_EVIDENCE = "gerber_x2_pin_number"
_X2_PIN_FUNCTION_EVIDENCE = "gerber_x2_pin_function"


def _trusted_pad_evidence_values(pad, kind):
    return tuple(
        sorted(
            {
                str(item.detail)
                for item in getattr(pad.provenance, "evidence", ())
                if item.kind == kind and item.confidence == 1.0
            }
        )
    )


def x2_component_export_plan(board):
    """Plan exact multi-pad KiCad footprints from source-proven Gerber X2 .P data.

    Only source-proven component hypotheses with one unambiguous refdes, one
    unique trusted pin number per pad, one surface side, and individually
    exportable pad geometry are grouped. Anything ambiguous is returned as a
    rejected identity group so callers can fall back to independent pad export
    without inventing component semantics.
    """
    source_components = [
        component
        for component in getattr(board, "components", ())
        if getattr(component, "kind", None) == "gerber_x2_component"
    ]
    pad_claims = Counter(
        str(pad_id)
        for component in source_components
        for pad_id in getattr(component, "pad_ids", ())
    )
    duplicate_object_ids = set(kicad_duplicate_object_ids(board))
    pad_by_id = {
        str(pad.id): pad
        for pad in getattr(board, "pads", ())
        if str(pad.id) not in duplicate_object_ids
    }

    groups = []
    rejected = []
    for component in sorted(source_components, key=lambda item: str(item.id)):
        component_id = str(component.id)
        reference = getattr(component, "reference", None)
        pad_ids = [str(pad_id) for pad_id in getattr(component, "pad_ids", ())]
        reasons = []

        if getattr(component, "confidence", None) != 1.0:
            reasons.append("component confidence is not source-certain")
        if not isinstance(reference, str) or not reference:
            reasons.append("component reference is missing")
        if not pad_ids:
            reasons.append("component has no pads")
        if len(set(pad_ids)) != len(pad_ids):
            reasons.append("component repeats a pad ID")
        if any(pad_claims[pad_id] != 1 for pad_id in pad_ids):
            reasons.append("one or more pads are claimed by multiple X2 components")

        missing = sorted(pad_id for pad_id in pad_ids if pad_id not in pad_by_id)
        if missing:
            reasons.append("missing or ambiguous pad IDs: " + ", ".join(missing))

        rows = []
        for pad_id in pad_ids:
            pad = pad_by_id.get(pad_id)
            if pad is None:
                continue
            status = pad_export_status(board, pad)
            if status != "export":
                reasons.append(f"{pad_id} is not exactly exportable ({status})")
                continue

            refdes_values = tuple(
                value
                for value in _trusted_pad_evidence_values(
                    pad, _X2_REFDES_EVIDENCE
                )
                if value
            )
            if refdes_values != (reference,):
                reasons.append(
                    f"{pad_id} does not carry exactly the component refdes"
                )

            pin_values = tuple(
                value
                for value in _trusted_pad_evidence_values(
                    pad, _X2_PIN_EVIDENCE
                )
                if value
            )
            if len(pin_values) != 1:
                reasons.append(
                    f"{pad_id} does not carry exactly one trusted pin number"
                )
                continue

            function_values = tuple(
                value
                for value in _trusted_pad_evidence_values(
                    pad, _X2_PIN_FUNCTION_EVIDENCE
                )
                if value
            )
            if len(function_values) > 1:
                reasons.append(
                    f"{pad_id} carries conflicting trusted pin functions"
                )

            descriptor, _ref_layer, _warning = pad_export_descriptor(pad)
            rows.append(
                {
                    "pad": pad,
                    "pad_id": pad_id,
                    "number": pin_values[0],
                    "function": (
                        function_values[0]
                        if len(function_values) == 1
                        else None
                    ),
                    "descriptor": descriptor,
                }
            )

        if len(rows) == len(pad_ids):
            pin_numbers = [row["number"] for row in rows]
            if len(set(pin_numbers)) != len(pin_numbers):
                reasons.append(
                    "trusted X2 pin numbers are not unique within the component"
                )
            footprint_layers = {
                row["descriptor"]["footprint_layer"] for row in rows
            }
            if len(footprint_layers) != 1:
                reasons.append("component pads do not share one surface side")
            elif next(iter(footprint_layers)) not in {"F.Cu", "B.Cu"}:
                reasons.append("component is not on a supported surface side")

        if reasons:
            rejected.append(
                {
                    "component_id": component_id,
                    "reference": reference,
                    "pad_ids": tuple(sorted(pad_ids)),
                    "reasons": tuple(sorted(set(reasons))),
                }
            )
            continue

        rows.sort(key=lambda row: row["pad_id"])
        origin = (
            float(rows[0]["pad"].center.x),
            float(rows[0]["pad"].center.y),
        )
        footprint_layer = rows[0]["descriptor"]["footprint_layer"]
        planned_pads = []
        for row in rows:
            pad = row["pad"]
            planned_pads.append(
                {
                    "pad_id": row["pad_id"],
                    "number": row["number"],
                    "function": row["function"],
                    "net_id": getattr(pad, "net_id", None),
                    "at": (
                        float(pad.center.x) - origin[0],
                        float(pad.center.y) - origin[1],
                    ),
                    "descriptor": row["descriptor"],
                }
            )

        groups.append(
            {
                "component_id": component_id,
                "reference": reference,
                "footprint_layer": footprint_layer,
                "reference_layer": (
                    "B.SilkS" if footprint_layer == "B.Cu" else "F.SilkS"
                ),
                "origin": origin,
                "pads": tuple(planned_pads),
            }
        )

    return tuple(groups), tuple(rejected)


def track_export_status(board, track):
    try:
        sx = float(track.start.x)
        sy = float(track.start.y)
        ex = float(track.end.x)
        ey = float(track.end.y)
    except (TypeError, ValueError):
        return "skip-invalid-coordinate"
    if not all(isfinite(value) for value in (sx, sy, ex, ey)):
        return "skip-invalid-coordinate"

    try:
        width = float(track.width)
    except (TypeError, ValueError):
        return "skip-invalid-width"
    if not isfinite(width) or width <= 0:
        return "skip-invalid-width"

    if sx == ex and sy == ey:
        return "skip-zero-length"
    if str(track.layer) not in declared_copper_layer_names(board):
        return "skip-layer"
    return "export"


def outline_export_status(segment):
    try:
        sx = float(segment.start.x)
        sy = float(segment.start.y)
        ex = float(segment.end.x)
        ey = float(segment.end.y)
    except (TypeError, ValueError):
        return "skip-invalid-coordinate"
    if not all(isfinite(value) for value in (sx, sy, ex, ey)):
        return "skip-invalid-coordinate"
    if sx == ex and sy == ey:
        return "skip-zero-length"
    return "export"


def drill_export_status(drill):
    try:
        diameter = float(drill.diameter)
    except (TypeError, ValueError):
        return "skip-invalid-geometry"
    if not isfinite(diameter) or diameter <= 0:
        return "skip-invalid-geometry"

    plating = str(getattr(drill, "plating", "unknown")).lower().replace("_", "-")
    if plating == "non-plated":
        return "export-npth"
    if plating == "unknown":
        return "skip-unknown-plating"
    if plating == "plated":
        return "skip-plated-padstack"
    return "skip-unsupported-plating"


def slot_geometry(slot):return slot_geometry_descriptor(slot)
def slot_export_status(slot):
    plating=str(getattr(slot,"plated","unknown")).lower().replace("_","-")
    if plating=="non-plated":return "export-npth"
    if plating=="plated":return "infer-plated-padstack"
    return "skip-unknown-plating"


_VIA_GEOMETRY_TOLERANCE_MM = 1e-6


def _proven_via_span_metadata(board):
    metadata = getattr(board, "metadata", {}) or {}
    if not isinstance(metadata, dict):
        return (), (("via_spans", "board metadata must be a mapping"),)
    raw_spans = metadata.get("via_spans", ())
    if raw_spans is None:
        return (), ()
    if not isinstance(raw_spans, (list, tuple)):
        return (), (("via_spans", "via_spans metadata must be a list or tuple"),)
    return raw_spans, ()


def _via_layer_order(board):
    return tuple(
        row["name"]
        for row in kicad_board_layer_specs(board)
        if str(row["name"]).endswith(".Cu")
    )


def proven_via_span_export_plan(board):
    """Return exactly representable proven via spans, omissions, and metadata errors.

    A KiCad via is emitted only when the proven span can be represented without
    inventing annular copper: one circular pad of identical diameter is present
    on every declared copper layer in the span, all supporting pads are centered
    on the plated drill, and all supporting pads resolve to one exported net.
    """
    raw_spans, problems = _proven_via_span_metadata(board)
    problems = list(problems)
    if problems:
        return (), (), tuple(problems)

    drill_by_id = {str(item.id): item for item in getattr(board, "drills", ())}
    pad_by_id = {str(item.id): item for item in getattr(board, "pads", ())}
    duplicate_object_ids = set(kicad_duplicate_object_ids(board))
    net_rows, duplicate_net_ids = kicad_net_export_rows(board)
    exported_net_ids = {row["id"] for row in net_rows}
    duplicate_net_ids = set(duplicate_net_ids)
    layer_order = _via_layer_order(board)
    layer_index = {name: index for index, name in enumerate(layer_order)}

    exportable = []
    omitted = []
    seen = set()

    def omit(drill_id, code, message):
        omitted.append((str(drill_id), code, message))

    for index, span in enumerate(raw_spans):
        metadata_id = f"via_spans[{index}]"
        if not isinstance(span, dict):
            problems.append((metadata_id, "via-span metadata entry must be a mapping"))
            continue
        proven = span.get("proven", False)
        if not isinstance(proven, bool):
            problems.append((metadata_id, "via-span proven flag must be boolean"))
            continue
        if not proven:
            continue

        drill_id = span.get("drill_id")
        from_layer = span.get("from_layer")
        to_layer = span.get("to_layer")
        pad_ids = span.get("pad_ids", ())

        if not isinstance(drill_id, str) or not drill_id:
            problems.append((metadata_id, "proven via span requires a non-empty drill_id"))
            continue
        if drill_id in seen:
            problems.append((drill_id, "duplicate proven via-span drill ID"))
            continue
        seen.add(drill_id)

        if (
            not isinstance(from_layer, str)
            or not from_layer
            or not isinstance(to_layer, str)
            or not to_layer
            or from_layer == to_layer
        ):
            problems.append(
                (drill_id, "proven via span requires two distinct non-empty copper layers")
            )
            continue
        if (
            not isinstance(pad_ids, (list, tuple))
            or len(pad_ids) < 2
            or any(not isinstance(pad_id, str) or not pad_id for pad_id in pad_ids)
        ):
            problems.append(
                (drill_id, "proven via span requires at least two supporting pad IDs")
            )
            continue
        if len(set(pad_ids)) != len(pad_ids):
            problems.append((drill_id, "proven via span supporting pad IDs must be unique"))
            continue

        drill = drill_by_id.get(drill_id)
        plating = (
            str(getattr(drill, "plating", "unknown")).lower().replace("_", "-")
            if drill is not None
            else "unknown"
        )
        if drill is None or plating != "plated":
            problems.append(
                (drill_id, "proven via span must reference an existing plated drill")
            )
            continue

        missing_pads = sorted({pad_id for pad_id in pad_ids if pad_id not in pad_by_id})
        if missing_pads:
            problems.append(
                (
                    drill_id,
                    "proven via span references missing supporting pads: "
                    + ", ".join(missing_pads),
                )
            )
            continue

        if drill_id in duplicate_object_ids:
            omit(
                drill_id,
                "KICAD_PROVEN_VIA_SOURCE_AMBIGUOUS",
                "proven via drill ID is duplicated in source objects; via omitted",
            )
            continue
        if any(pad_id in duplicate_object_ids for pad_id in pad_ids):
            omit(
                drill_id,
                "KICAD_PROVEN_VIA_SUPPORT_AMBIGUOUS",
                "one or more supporting pad IDs are duplicated in source objects; via omitted",
            )
            continue

        if from_layer not in layer_index or to_layer not in layer_index:
            omit(
                drill_id,
                "KICAD_PROVEN_VIA_LAYER_UNSUPPORTED",
                "proven via span endpoint is not a declared canonical KiCad copper layer",
            )
            continue

        start_index, end_index = sorted(
            (layer_index[from_layer], layer_index[to_layer])
        )
        start_layer = layer_order[start_index]
        end_layer = layer_order[end_index]
        expected_layers = layer_order[start_index : end_index + 1]

        via_type = "through"
        x2_span_kind = str(
            getattr(drill, "x2_span_kind", "") or ""
        ).lower()
        canonical_span = getattr(drill, "layer_span", None)
        span_proven = getattr(drill, "span_proven", False) is True
        is_full_through = (
            start_index == 0
            and end_index == len(layer_order) - 1
            and {start_layer, end_layer} == {"F.Cu", "B.Cu"}
        )

        if is_full_through:
            if x2_span_kind and x2_span_kind != "pth":
                omit(
                    drill_id,
                    "KICAD_PROVEN_VIA_X2_KIND_MISMATCH",
                    "full-stack plated via conflicts with explicit X2 drill span kind; via omitted instead of overriding source evidence",
                )
                continue
        else:
            if x2_span_kind not in {"blind", "buried"}:
                omit(
                    drill_id,
                    "KICAD_PROVEN_VIA_TYPE_UNPROVEN",
                    "partial-layer plated span lacks explicit X2 Blind/Buried evidence; via omitted instead of guessing blind versus microvia semantics",
                )
                continue
            if (
                not span_proven
                or not isinstance(canonical_span, (list, tuple))
                or len(canonical_span) != 2
                or {str(canonical_span[0]), str(canonical_span[1])}
                != {start_layer, end_layer}
            ):
                omit(
                    drill_id,
                    "KICAD_PROVEN_VIA_X2_SPAN_UNPROVEN",
                    "partial-layer via requires a source-proven canonical drill span matching the exported layer endpoints",
                )
                continue

            surface_endpoints = sum(
                layer in {"F.Cu", "B.Cu"}
                for layer in (start_layer, end_layer)
            )
            if (
                (x2_span_kind == "blind" and surface_endpoints != 1)
                or (x2_span_kind == "buried" and surface_endpoints != 0)
            ):
                omit(
                    drill_id,
                    "KICAD_PROVEN_VIA_X2_KIND_MISMATCH",
                    "explicit X2 Blind/Buried kind is inconsistent with the proven canonical layer endpoints",
                )
                continue

            # KiCad serializes both blind and buried vias with the blind
            # via type; endpoint layers distinguish surface-reaching
            # blind vias from fully internal buried vias.
            via_type = x2_span_kind

        support = [pad_by_id[pad_id] for pad_id in pad_ids]
        by_layer = {}
        for pad in support:
            by_layer.setdefault(str(pad.layer), []).append(pad)
        if set(by_layer) != set(expected_layers) or any(
            len(by_layer.get(layer, ())) != 1 for layer in expected_layers
        ):
            omit(
                drill_id,
                "KICAD_PROVEN_VIA_LAYER_SUPPORT_INCOMPLETE",
                "exact KiCad via export requires exactly one supporting pad on every copper layer in the proven span",
            )
            continue

        try:
            cx = float(drill.center.x)
            cy = float(drill.center.y)
            drill_diameter = float(drill.diameter)
        except (TypeError, ValueError):
            omit(
                drill_id,
                "KICAD_PROVEN_VIA_GEOMETRY_INVALID",
                "plated drill center and diameter must be finite numeric values",
            )
            continue
        if (
            not all(isfinite(value) for value in (cx, cy, drill_diameter))
            or drill_diameter <= 0
        ):
            omit(
                drill_id,
                "KICAD_PROVEN_VIA_GEOMETRY_INVALID",
                "plated drill center must be finite and drill diameter must be finite and positive",
            )
            continue

        diameters = []
        geometry_ok = True
        for layer in expected_layers:
            pad = by_layer[layer][0]
            if str(getattr(pad, "shape", "")).upper() != "C":
                geometry_ok = False
                break
            try:
                px = float(pad.center.x)
                py = float(pad.center.y)
                sx = float(pad.size_x)
                sy = float(pad.size_y)
            except (TypeError, ValueError):
                geometry_ok = False
                break
            if (
                not all(isfinite(value) for value in (px, py, sx, sy))
                or sx <= 0
                or sy <= 0
                or abs(px - cx) > _VIA_GEOMETRY_TOLERANCE_MM
                or abs(py - cy) > _VIA_GEOMETRY_TOLERANCE_MM
                or abs(sx - sy) > _VIA_GEOMETRY_TOLERANCE_MM
            ):
                geometry_ok = False
                break
            diameters.append(sx)

        if (
            not geometry_ok
            or not diameters
            or max(diameters) - min(diameters) > _VIA_GEOMETRY_TOLERANCE_MM
            or diameters[0] <= drill_diameter + _VIA_GEOMETRY_TOLERANCE_MM
        ):
            omit(
                drill_id,
                "KICAD_PROVEN_VIA_ANNULUS_UNREPRESENTABLE",
                "exact KiCad via export requires concentric circular supporting pads with one identical annular diameter larger than the drill on every spanned copper layer",
            )
            continue

        net_ids = {getattr(pad, "net_id", None) for pad in support}
        if len(net_ids) != 1:
            omit(
                drill_id,
                "KICAD_PROVEN_VIA_NET_CONFLICT",
                "supporting pads do not agree on one reconstructed net",
            )
            continue
        net_id = next(iter(net_ids))
        if (
            net_id is None
            or net_id in duplicate_net_ids
            or net_id not in exported_net_ids
        ):
            omit(
                drill_id,
                "KICAD_PROVEN_VIA_NET_UNRESOLVED",
                "proven via span does not resolve to one unambiguous exported net",
            )
            continue

        exportable.append(
            {
                "drill_id": drill_id,
                "at": (cx, cy),
                "size": diameters[0],
                "drill": drill_diameter,
                "layers": (start_layer, end_layer),
                "via_type": via_type,
                "net_id": net_id,
                "pad_ids": tuple(sorted(pad_ids)),
            }
        )

    exportable.sort(key=lambda item: item["drill_id"])
    omitted.sort(key=lambda item: item[0])
    return tuple(exportable), tuple(omitted), tuple(problems)


def proven_via_span_omissions(board):
    """Backward-compatible view of proven via spans that remain unexportable."""
    _exportable, omitted, problems = proven_via_span_export_plan(board)
    return tuple(item[0] for item in omitted), problems

