import re
from collections import Counter
from math import isfinite

KICAD_DEFAULT_BOARD_THICKNESS_MM = 1.6
KICAD_DEFAULT_PAD_TO_MASK_CLEARANCE_MM = 0.0


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


def proven_via_span_omissions(board):
    """Return proven via-span drill IDs plus malformed metadata diagnostics."""
    metadata = getattr(board, "metadata", {}) or {}
    if not isinstance(metadata, dict):
        return (), (("via_spans", "board metadata must be a mapping"),)
    raw_spans = metadata.get("via_spans", ())
    if raw_spans is None:
        return (), ()
    if not isinstance(raw_spans, (list, tuple)):
        return (), (("via_spans", "via_spans metadata must be a list or tuple"),)

    drill_by_id = {str(item.id): item for item in getattr(board, "drills", ())}
    pad_by_id = {str(item.id): item for item in getattr(board, "pads", ())}
    omitted = []
    problems = []
    seen = set()

    for index, span in enumerate(raw_spans):
        object_id = f"via_spans[{index}]"
        if not isinstance(span, dict):
            problems.append((object_id, "via-span metadata entry must be a mapping"))
            continue
        proven = span.get("proven", False)
        if not isinstance(proven, bool):
            problems.append((object_id, "via-span proven flag must be boolean"))
            continue
        if not proven:
            continue

        drill_id = span.get("drill_id")
        from_layer = span.get("from_layer")
        to_layer = span.get("to_layer")
        pad_ids = span.get("pad_ids", ())
        if not isinstance(drill_id, str) or not drill_id:
            problems.append((object_id, "proven via span requires a non-empty drill_id"))
            continue
        object_id = drill_id
        if (
            not isinstance(from_layer, str)
            or not from_layer
            or not isinstance(to_layer, str)
            or not to_layer
            or from_layer == to_layer
        ):
            problems.append(
                (object_id, "proven via span requires two distinct non-empty copper layers")
            )
            continue
        if (
            not isinstance(pad_ids, (list, tuple))
            or len(pad_ids) < 2
            or any(not isinstance(pad_id, str) or not pad_id for pad_id in pad_ids)
        ):
            problems.append(
                (object_id, "proven via span requires at least two supporting pad IDs")
            )
            continue

        drill = drill_by_id.get(drill_id)
        plating = str(getattr(drill, "plating", "unknown")).lower().replace("_", "-")
        if drill is None or plating != "plated":
            problems.append(
                (object_id, "proven via span must reference an existing plated drill")
            )
            continue

        missing_pads = sorted({pad_id for pad_id in pad_ids if pad_id not in pad_by_id})
        if missing_pads:
            problems.append(
                (
                    object_id,
                    "proven via span references missing supporting pads: "
                    + ", ".join(missing_pads),
                )
            )
            continue

        supporting_layers = {str(pad_by_id[pad_id].layer) for pad_id in pad_ids}
        if from_layer not in supporting_layers or to_layer not in supporting_layers:
            problems.append(
                (
                    object_id,
                    "proven via span endpoints are not both supported by referenced pads",
                )
            )
            continue
        if drill_id in seen:
            problems.append((object_id, "duplicate proven via-span drill ID"))
            continue
        seen.add(drill_id)
        omitted.append(drill_id)

    return tuple(sorted(omitted)), tuple(problems)
