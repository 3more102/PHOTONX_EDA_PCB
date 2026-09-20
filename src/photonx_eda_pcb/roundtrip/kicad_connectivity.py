from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ..exporters.kicad_policy import pad_export_descriptor, proven_via_span_omissions, slot_export_status
from ..kicad_reader import read_kicad_board_text
from ..kicad_identity import photonx_uuid
from ..plated_slot_inference import infer_plated_slot_padstack
from .mechanical import compare_mechanical_slots
from .regions import compare_kicad_copper_regions


_RECOVERED_PAD_FOOTPRINT = "PHOTONX:RecoveredPad"
_RECOVERED_NPTH_SLOT = "PHOTONX:RecoveredNPTHSlot"
_RECOVERED_PLATED_SLOT = "PHOTONX:RecoveredPlatedSlot"


def _r(value):
    return round(float(value), 6)


def _point(value):
    if value is None or len(value) < 2:
        raise ValueError("point must contain x/y coordinates")
    return (_r(value[0]), _r(value[1]))


def _stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _compare_multiset(expected, observed):
    expected_keys = [_stable(item) for item in expected]
    observed_keys = [_stable(item) for item in observed]
    expected_count = Counter(expected_keys)
    observed_count = Counter(observed_keys)

    missing = []
    for key, count in sorted((expected_count - observed_count).items()):
        missing.extend(json.loads(key) for _ in range(count))

    unexpected = []
    for key, count in sorted((observed_count - expected_count).items()):
        unexpected.extend(json.loads(key) for _ in range(count))

    return {
        "equal": expected_count == observed_count,
        "expected_count": len(expected),
        "observed_count": len(observed),
        "missing": missing,
        "unexpected": unexpected,
    }


def _net_rows_from_board(board):
    rows = [{"code": 0, "name": ""}]
    for code, net in enumerate(board.nets, start=1):
        rows.append({"code": code, "name": str(net.label or net.id)})
    return rows


def _source_net_binding(board, net_id):
    if net_id is None:
        return {"code": 0, "name": ""}
    for code, net in enumerate(board.nets, start=1):
        if net.id == net_id:
            return {"code": code, "name": str(net.label or net.id)}
    return None


def _observed_net_lookup(readback, issues):
    lookup = {}
    counts = Counter()
    for row in readback.get("nets", ()):
        code = int(row["code"])
        name = str(row["name"])
        counts[code] += 1
        lookup[code] = name

    duplicate_codes = sorted(code for code, count in counts.items() if count > 1)
    if duplicate_codes:
        issues.append(
            {
                "code": "KICAD_ROUNDTRIP_DUPLICATE_NET_CODES",
                "net_codes": duplicate_codes,
            }
        )
    return lookup


def _binding_from_code(code, lookup, issues, object_kind, object_id):
    if code in (None, 0):
        return {"code": 0, "name": ""}
    code = int(code)
    if code not in lookup:
        issues.append(
            {
                "code": "KICAD_ROUNDTRIP_UNKNOWN_NET_CODE",
                "object_kind": object_kind,
                "object_id": str(object_id),
                "net_code": code,
            }
        )
        return {"code": code, "name": None}
    return {"code": code, "name": str(lookup[code])}


def _check_embedded_net_name(item, binding, issues, object_kind, object_id):
    embedded = item.get("net_name")
    if binding["code"] == 0:
        if embedded not in (None, ""):
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_UNASSIGNED_NET_NAME",
                    "object_kind": object_kind,
                    "object_id": str(object_id),
                    "net_name": str(embedded),
                }
            )
        return
    if embedded is None or str(embedded) != binding["name"]:
        issues.append(
            {
                "code": "KICAD_ROUNDTRIP_NET_NAME_MISMATCH",
                "object_kind": object_kind,
                "object_id": str(object_id),
                "expected_name": binding["name"],
                "observed_name": None if embedded is None else str(embedded),
            }
        )


def _declared_track_layers(board):
    highest = 0
    for obj in [*board.tracks, *board.pads, *getattr(board, "regions", ())]:
        layer = str(getattr(obj, "layer", ""))
        if not (layer.startswith("In") and layer.endswith(".Cu")):
            continue
        digits = layer[2:-3]
        if digits.isdigit() and 1 <= int(digits) <= 30:
            highest = max(highest, int(digits))
    return {"F.Cu", "B.Cu"} | {
        f"In{index}.Cu" for index in range(1, highest + 1)
    }


def _reported_sets(source_ids, exported_ids, skipped_ids, family, issues):
    source = set(source_ids)
    exported = set(exported_ids)
    skipped = set(skipped_ids)

    overlap = sorted(exported & skipped)
    if overlap:
        issues.append(
            {
                "code": f"KICAD_ROUNDTRIP_{family}_REPORT_OVERLAP",
                "object_ids": overlap,
            }
        )

    unknown = sorted((exported | skipped) - source)
    if unknown:
        issues.append(
            {
                "code": f"KICAD_ROUNDTRIP_{family}_REPORT_UNKNOWN_IDS",
                "object_ids": unknown,
            }
        )

    undecided = sorted(source - exported - skipped)
    if undecided:
        issues.append(
            {
                "code": f"KICAD_ROUNDTRIP_{family}_REPORT_MISSING_IDS",
                "object_ids": undecided,
            }
        )

    return exported & source, skipped & source


def _reported_track_sets(board, export_report, issues):
    source_ids = {track.id for track in board.tracks}
    if export_report is None:
        declared_layers = _declared_track_layers(board)
        exported = {
            track.id
            for track in board.tracks
            if _source_net_binding(board, track.net_id) is not None
            and str(track.layer) in declared_layers
        }
        return exported, source_ids - exported

    return _reported_sets(
        source_ids,
        getattr(export_report, "exported_track_ids", ()),
        getattr(export_report, "skipped_track_ids", ()),
        "TRACK",
        issues,
    )


def _track_item(start, end, width, layer, binding, object_uuid):
    a, b = sorted((_point(start), _point(end)))
    return {
        "start": list(a),
        "end": list(b),
        "width": _r(width),
        "layer": str(layer),
        "net": binding,
        "uuid": None if object_uuid is None else str(object_uuid),
    }


def _expected_tracks(board, exported_track_ids, issues):
    out = []
    for track in board.tracks:
        if track.id not in exported_track_ids:
            continue
        binding = _source_net_binding(board, track.net_id)
        if binding is None:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_EXPORTED_TRACK_NET_UNRESOLVED",
                    "track_id": track.id,
                    "net_id": track.net_id,
                }
            )
            continue
        out.append(
            _track_item(
                (track.start.x, track.start.y),
                (track.end.x, track.end.y),
                track.width,
                track.layer,
                binding,
                photonx_uuid("track:" + str(track.id)),
            )
        )
    return out


def _observed_tracks(readback, net_lookup, issues):
    out = []
    for index, segment in enumerate(readback.get("segments", ())):
        try:
            binding = _binding_from_code(
                segment.get("net"),
                net_lookup,
                issues,
                "segment",
                index,
            )
            out.append(
                _track_item(
                    segment.get("start"),
                    segment.get("end"),
                    segment.get("width"),
                    segment.get("layer"),
                    binding,
                    segment.get("uuid"),
                )
            )
        except (TypeError, ValueError, IndexError, KeyError) as exc:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_INVALID_SEGMENT",
                    "segment_index": index,
                    "detail": str(exc),
                }
            )
    return out


def _via_item(at, size, drill, layers, binding):
    return {
        "at": list(_point(at)),
        "size": _r(size),
        "drill": _r(drill),
        "layers": [str(layer) for layer in layers],
        "net": binding,
    }


def _observed_vias(readback, net_lookup, issues):
    out = []
    for index, via in enumerate(readback.get("vias", ())):
        try:
            binding = _binding_from_code(
                via.get("net"),
                net_lookup,
                issues,
                "via",
                index,
            )
            out.append(
                _via_item(
                    via.get("at"),
                    via.get("size"),
                    via.get("drill"),
                    via.get("layers", ()),
                    binding,
                )
            )
        except (TypeError, ValueError, IndexError, KeyError) as exc:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_INVALID_VIA",
                    "via_index": index,
                    "detail": str(exc),
                }
            )
    return out


def _pad_geometry_item(
    footprint_at,
    footprint_angle,
    footprint_layer,
    pad_number,
    pad_kind,
    pad_shape,
    pad_at,
    pad_angle,
    pad_size,
    drill_shape,
    drill_size,
    drill_offset,
    layers,
):
    return {
        "footprint_at": list(_point(footprint_at)),
        "footprint_angle": _r(footprint_angle),
        "footprint_layer": str(footprint_layer),
        "number": str(pad_number),
        "kind": str(pad_kind),
        "shape": str(pad_shape),
        "pad_at": list(_point(pad_at)),
        "pad_angle": _r(pad_angle),
        "size": list(_point(pad_size)),
        "drill_shape": None if drill_shape is None else str(drill_shape),
        "drill_size": None if drill_size is None else list(_point(drill_size)),
        "drill_offset": list(_point(drill_offset)),
        "layers": sorted(str(layer) for layer in layers),
    }


def _expected_pad_geometry(pad):
    descriptor, _ref_layer, _warning = pad_export_descriptor(pad)
    return _pad_geometry_item(
        (pad.center.x, pad.center.y),
        0.0,
        descriptor["footprint_layer"],
        descriptor["number"],
        descriptor["kind"],
        descriptor["shape"],
        descriptor["pad_at"],
        descriptor["pad_angle"],
        descriptor["size"],
        descriptor["drill_shape"],
        descriptor["drill_size"],
        descriptor["drill_offset"],
        descriptor["layers"],
    )


def _observed_pad_geometry(footprint, pad):
    return _pad_geometry_item(
        footprint.get("at"),
        footprint.get("angle", 0.0),
        footprint.get("layer"),
        pad.get("number"),
        pad.get("kind"),
        pad.get("shape"),
        pad.get("at"),
        pad.get("angle", 0.0),
        pad.get("size"),
        pad.get("drill_shape"),
        pad.get("drill_size"),
        pad.get("drill_offset", (0.0, 0.0)),
        pad.get("layers", ()),
    )


def _expected_pads(board):
    out = []
    unresolved = []
    for pad in board.pads:
        binding = _source_net_binding(board, pad.net_id)
        if binding is None:
            unresolved.append(pad.id)
            binding = {"code": 0, "name": ""}
        out.append(
            {
                "id": str(pad.id),
                "uuid": photonx_uuid("fp:" + str(pad.id)),
                "pad_uuid": photonx_uuid("pad:" + str(pad.id)),
                "geometry": _expected_pad_geometry(pad),
                "net": binding,
            }
        )
    return out, sorted(unresolved)


def _observed_pads(readback, net_lookup, issues):
    out = []
    for fp_index, footprint in enumerate(readback.get("footprints", ())):
        if footprint.get("name") != _RECOVERED_PAD_FOOTPRINT:
            continue
        reference = footprint.get("reference")
        pads = list(footprint.get("pads", ()))
        if not reference:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_PAD_REFERENCE_MISSING",
                    "footprint_index": fp_index,
                }
            )
            continue
        if len(pads) != 1:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_PAD_COUNT_INVALID",
                    "pad_id": str(reference),
                    "pad_count": len(pads),
                }
            )
            continue

        try:
            geometry = _observed_pad_geometry(footprint, pads[0])
        except (TypeError, ValueError, IndexError, KeyError) as exc:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_INVALID_PAD_GEOMETRY",
                    "pad_id": str(reference),
                    "detail": str(exc),
                }
            )
            continue

        binding = _binding_from_code(
            pads[0].get("net"),
            net_lookup,
            issues,
            "pad",
            reference,
        )
        _check_embedded_net_name(
            pads[0],
            binding,
            issues,
            "pad",
            reference,
        )
        out.append(
            {
                "id": str(reference),
                "uuid": footprint.get("uuid"),
                "pad_uuid": pads[0].get("uuid"),
                "geometry": geometry,
                "net": binding,
            }
        )
    return out


def _expected_regions(board, exported_ids, issues):
    out = []
    for region in getattr(board, "regions", ()):
        if region.id not in exported_ids:
            continue
        binding = _source_net_binding(board, region.net_id)
        if binding is None:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_EXPORTED_REGION_NET_UNRESOLVED",
                    "region_id": region.id,
                    "net_id": region.net_id,
                }
            )
            continue
        out.append(
            {
                "id": str(region.id),
                "uuid": photonx_uuid("region:" + str(region.id)),
                "net": binding,
            }
        )
    return out


def _observed_regions(readback, net_lookup, issues):
    out = []
    for index, zone in enumerate(readback.get("zones", ())):
        name = zone.get("name")
        if not isinstance(name, str) or not name.startswith("PHOTONX:"):
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_REGION_IDENTITY_MISSING",
                    "zone_index": index,
                    "zone_name": name,
                }
            )
            continue
        region_id = name[len("PHOTONX:") :]
        binding = _binding_from_code(
            zone.get("net"),
            net_lookup,
            issues,
            "zone",
            region_id,
        )
        _check_embedded_net_name(
            zone,
            binding,
            issues,
            "zone",
            region_id,
        )
        out.append(
            {
                "id": region_id,
                "uuid": zone.get("uuid"),
                "net": binding,
            }
        )
    return out


def _expected_slots(board, exported_ids, issues):
    out = []
    unresolved = []
    for slot in getattr(board, "slots", ()):
        if slot.id not in exported_ids:
            continue

        status = slot_export_status(slot)
        if status == "export-npth":
            out.append(
                {
                    "id": str(slot.id),
                    "uuid": photonx_uuid("slot-fp:" + str(slot.id)),
                    "pad_uuid": photonx_uuid("slot-pad:" + str(slot.id)),
                    "kind": "npth",
                    "net": {"code": 0, "name": ""},
                }
            )
            continue

        if status != "infer-plated-padstack":
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_EXPORTED_SLOT_POLICY_INVALID",
                    "slot_id": slot.id,
                    "status": status,
                }
            )
            continue

        inference = infer_plated_slot_padstack(board, slot)
        if inference.padstack is None:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_EXPORTED_SLOT_PADSTACK_MISSING",
                    "slot_id": slot.id,
                    "blockers": list(inference.blockers),
                }
            )
            continue

        binding = _source_net_binding(board, inference.padstack.net_id)
        if binding is None:
            unresolved.append(slot.id)
            binding = {"code": 0, "name": ""}
        out.append(
            {
                "id": str(slot.id),
                "uuid": photonx_uuid("slot-fp:" + str(slot.id)),
                "pad_uuid": photonx_uuid("slot-pad:" + str(slot.id)),
                "kind": "plated",
                "net": binding,
            }
        )
    return out, sorted(unresolved)


def _observed_slots(readback, net_lookup, issues):
    out = []
    names = {
        _RECOVERED_NPTH_SLOT: "npth",
        _RECOVERED_PLATED_SLOT: "plated",
    }
    for fp_index, footprint in enumerate(readback.get("footprints", ())):
        kind = names.get(footprint.get("name"))
        if kind is None:
            continue
        reference = footprint.get("reference")
        pads = list(footprint.get("pads", ()))
        if not reference:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_SLOT_REFERENCE_MISSING",
                    "footprint_index": fp_index,
                    "kind": kind,
                }
            )
            continue
        if len(pads) != 1:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_SLOT_PAD_COUNT_INVALID",
                    "slot_id": str(reference),
                    "pad_count": len(pads),
                }
            )
            continue

        binding = _binding_from_code(
            pads[0].get("net"),
            net_lookup,
            issues,
            "slot",
            reference,
        )
        _check_embedded_net_name(
            pads[0],
            binding,
            issues,
            "slot",
            reference,
        )
        out.append(
            {
                "id": str(reference),
                "uuid": footprint.get("uuid"),
                "pad_uuid": pads[0].get("uuid"),
                "kind": kind,
                "net": binding,
            }
        )
    return out


def _empty_comparison():
    return _compare_multiset([], [])


def compare_kicad_connectivity(board, readback, export_report=None):
    """Compare generated KiCad connectivity with the source/export policy.

    With an export report, the audit covers the net table plus tracks,
    rejects unexpected KiCad vias, and compares recovered pads, copper regions including canonical shell/hole geometry,
    and recovered slots, including canonical exported slot geometry. Proven plated via spans are tracked as explicit source
    export losses because the current exporter does not synthesize via annular
    geometry. Deterministic PhotonX UUIDs are part of the supported
    object identity for emitted tracks, recovered pad/slot footprints and their child pads, regions, and slots. Recovered-pad emitted geometry is compared exactly as read back.
    Without a report,
    the legacy fallback can still validate net/track/pad connectivity, but
    it fails closed when region or slot objects are present because their
    omission decisions cannot be reconstructed as reliably as the report.
    """

    issues = []
    source_via_span_ids, via_span_metadata_problems = proven_via_span_omissions(board)
    for object_id, message in via_span_metadata_problems:
        issues.append(
            {
                "code": "KICAD_ROUNDTRIP_VIA_SPAN_METADATA_INVALID",
                "object_id": object_id,
                "detail": message,
            }
        )
    net_lookup = _observed_net_lookup(readback, issues)

    nets = _compare_multiset(
        _net_rows_from_board(board),
        [
            {"code": int(row["code"]), "name": str(row["name"])}
            for row in readback.get("nets", ())
        ],
    )

    exported_track_ids, skipped_track_ids = _reported_track_sets(
        board,
        export_report,
        issues,
    )
    tracks = _compare_multiset(
        _expected_tracks(board, exported_track_ids, issues),
        _observed_tracks(readback, net_lookup, issues),
    )

    vias = _compare_multiset(
        [],
        _observed_vias(readback, net_lookup, issues),
    )

    expected_pads, unresolved_pad_ids = _expected_pads(board)
    pads = _compare_multiset(
        expected_pads,
        _observed_pads(readback, net_lookup, issues),
    )

    regions = _empty_comparison()
    region_geometry = compare_kicad_copper_regions(board, (), region_ids=())
    slots = _empty_comparison()
    slot_geometry = compare_mechanical_slots([], [])
    skipped_region_ids = set()
    skipped_slot_ids = set()
    unresolved_slot_ids = []
    if export_report is None:
        skipped_via_span_ids = set(source_via_span_ids)
    else:
        _, skipped_via_span_ids = _reported_sets(
            source_via_span_ids,
            (),
            getattr(export_report, "skipped_via_span_ids", ()),
            "VIA_SPAN",
            issues,
        )

    source_regions = list(getattr(board, "regions", ()))
    source_slots = list(getattr(board, "slots", ()))
    observed_regions = list(readback.get("zones", ()))
    observed_slot_footprints = [
        footprint
        for footprint in readback.get("footprints", ())
        if footprint.get("name")
        in {_RECOVERED_NPTH_SLOT, _RECOVERED_PLATED_SLOT}
    ]

    if export_report is None:
        if source_regions or observed_regions:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_EXPORT_REPORT_REQUIRED",
                    "object_family": "regions",
                }
            )
        if source_slots or observed_slot_footprints:
            issues.append(
                {
                    "code": "KICAD_ROUNDTRIP_EXPORT_REPORT_REQUIRED",
                    "object_family": "slots",
                }
            )
    else:
        exported_region_ids, skipped_region_ids = _reported_sets(
            (region.id for region in source_regions),
            getattr(export_report, "exported_region_ids", ()),
            getattr(export_report, "skipped_region_ids", ()),
            "REGION",
            issues,
        )
        regions = _compare_multiset(
            _expected_regions(board, exported_region_ids, issues),
            _observed_regions(readback, net_lookup, issues),
        )
        region_geometry = compare_kicad_copper_regions(
            board,
            observed_regions,
            region_ids=exported_region_ids,
        )

        exported_slot_ids, skipped_slot_ids = _reported_sets(
            (slot.id for slot in source_slots),
            getattr(export_report, "exported_slot_ids", ()),
            getattr(export_report, "skipped_slot_ids", ()),
            "SLOT",
            issues,
        )
        expected_slots, unresolved_slot_ids = _expected_slots(
            board,
            exported_slot_ids,
            issues,
        )
        slots = _compare_multiset(
            expected_slots,
            _observed_slots(readback, net_lookup, issues),
        )
        slot_geometry = compare_mechanical_slots(
            [
                slot
                for slot in source_slots
                if slot.id in exported_slot_ids
            ],
            readback.get("mechanical_slots", ()),
        )

    roundtrip_equal = bool(
        nets["equal"]
        and tracks["equal"]
        and vias["equal"]
        and pads["equal"]
        and regions["equal"]
        and region_geometry["equal"]
        and slots["equal"]
        and slot_geometry["equal"]
        and not issues
    )

    losses = {
        "skipped_track_ids": sorted(skipped_track_ids),
        "skipped_region_ids": sorted(skipped_region_ids),
        "skipped_slot_ids": sorted(skipped_slot_ids),
        "unresolved_pad_net_ids": unresolved_pad_ids,
        "unresolved_slot_net_ids": unresolved_slot_ids,
        "omitted_proven_via_span_drill_ids": sorted(skipped_via_span_ids),
    }
    source_connectivity_complete = not any(losses.values())

    return {
        "scope": [
            "net_table",
            "tracks",
            "vias",
            "recovered_pads",
            "copper_regions",
            "region_geometry",
            "recovered_slots",
            "slot_geometry",
        ],
        "roundtrip_equal": roundtrip_equal,
        "source_connectivity_complete": source_connectivity_complete,
        "source_equivalent": bool(
            roundtrip_equal and source_connectivity_complete
        ),
        "nets": nets,
        "tracks": tracks,
        "vias": vias,
        "pads": pads,
        "regions": regions,
        "region_geometry": region_geometry,
        "slots": slots,
        "slot_geometry": slot_geometry,
        "losses": losses,
        "issues": issues,
    }


def validate_kicad_connectivity_roundtrip(board, path, export_report=None):
    path = Path(path)
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    return compare_kicad_connectivity(board, readback, export_report)
