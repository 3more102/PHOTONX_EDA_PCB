from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ..exporters.kicad_policy import slot_export_status
from ..kicad_reader import read_kicad_board_text
from ..plated_slot_inference import infer_plated_slot_padstack


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


def _reported_sets(source_ids, exported_ids, skipped_ids, kind, issues):
    source_ids = set(source_ids)
    exported = set(exported_ids)
    skipped = set(skipped_ids)

    overlap = sorted(exported & skipped)
    if overlap:
        issues.append(
            {
                "code": f"KICAD_ROUNDTRIP_{kind}_REPORT_OVERLAP",
                "object_ids": overlap,
            }
        )

    unknown = sorted((exported | skipped) - source_ids)
    if unknown:
        issues.append(
            {
                "code": f"KICAD_ROUNDTRIP_{kind}_REPORT_UNKNOWN_IDS",
                "object_ids": unknown,
            }
        )

    undecided = sorted(source_ids - exported - skipped)
    if undecided:
        issues.append(
            {
                "code": f"KICAD_ROUNDTRIP_{kind}_REPORT_MISSING_IDS",
                "object_ids": undecided,
            }
        )

    return exported & source_ids, skipped & source_ids


def _track_item(start, end, width, layer, binding):
    a, b = sorted((_point(start), _point(end)))
    return {
        "start": list(a),
        "end": list(b),
        "width": _r(width),
        "layer": str(layer),
        "net": binding,
    }


def _expected_tracks(board, exported_ids, issues):
    out = []
    for track in board.tracks:
        if track.id not in exported_ids:
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


def _expected_pads(board):
    items = []
    unresolved = []
    for pad in board.pads:
        binding = _source_net_binding(board, pad.net_id)
        if binding is None:
            unresolved.append(pad.id)
            binding = {"code": 0, "name": ""}
        items.append({"id": str(pad.id), "net": binding})
    return items, sorted(unresolved)


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
        out.append(
            {
                "id": str(reference),
                "net": _binding_from_code(
                    pads[0].get("net"),
                    net_lookup,
                    issues,
                    "pad",
                    reference,
                ),
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
        out.append({"id": str(region.id), "net": binding})
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
        out.append(
            {
                "id": region_id,
                "net": _binding_from_code(
                    zone.get("net"),
                    net_lookup,
                    issues,
                    "zone",
                    region_id,
                ),
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
        out.append({"id": str(slot.id), "kind": "plated", "net": binding})
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
        out.append(
            {
                "id": str(reference),
                "kind": kind,
                "net": _binding_from_code(
                    pads[0].get("net"),
                    net_lookup,
                    issues,
                    "slot",
                    reference,
                ),
            }
        )
    return out


def compare_kicad_connectivity(board, readback, export_report):
    """Compare KiCad readback connectivity with the exact exporter policy.

    roundtrip_equal means the emitted KiCad file re-reads with the same net
    semantics for the objects the exporter said it emitted.

    source_equivalent is stronger: it additionally requires that the exporter
    did not intentionally omit source connectivity or suppress unresolved net
    references.
    """

    issues = []
    net_lookup = _observed_net_lookup(readback, issues)

    nets = _compare_multiset(
        _net_rows_from_board(board),
        [
            {"code": int(row["code"]), "name": str(row["name"])}
            for row in readback.get("nets", ())
        ],
    )

    exported_tracks, skipped_tracks = _reported_sets(
        (track.id for track in board.tracks),
        getattr(export_report, "exported_track_ids", ()),
        getattr(export_report, "skipped_track_ids", ()),
        "TRACK",
        issues,
    )
    tracks = _compare_multiset(
        _expected_tracks(board, exported_tracks, issues),
        _observed_tracks(readback, net_lookup, issues),
    )

    expected_pads, unresolved_pads = _expected_pads(board)
    pads = _compare_multiset(
        expected_pads,
        _observed_pads(readback, net_lookup, issues),
    )

    exported_regions, skipped_regions = _reported_sets(
        (region.id for region in getattr(board, "regions", ())),
        getattr(export_report, "exported_region_ids", ()),
        getattr(export_report, "skipped_region_ids", ()),
        "REGION",
        issues,
    )
    regions = _compare_multiset(
        _expected_regions(board, exported_regions, issues),
        _observed_regions(readback, net_lookup, issues),
    )

    exported_slots, skipped_slots = _reported_sets(
        (slot.id for slot in getattr(board, "slots", ())),
        getattr(export_report, "exported_slot_ids", ()),
        getattr(export_report, "skipped_slot_ids", ()),
        "SLOT",
        issues,
    )
    expected_slots, unresolved_slots = _expected_slots(
        board,
        exported_slots,
        issues,
    )
    slots = _compare_multiset(
        expected_slots,
        _observed_slots(readback, net_lookup, issues),
    )

    roundtrip_equal = bool(
        nets["equal"]
        and tracks["equal"]
        and pads["equal"]
        and regions["equal"]
        and slots["equal"]
        and not issues
    )

    losses = {
        "skipped_track_ids": sorted(skipped_tracks),
        "skipped_region_ids": sorted(skipped_regions),
        "skipped_slot_ids": sorted(skipped_slots),
        "unresolved_pad_net_ids": unresolved_pads,
        "unresolved_slot_net_ids": unresolved_slots,
    }
    source_connectivity_complete = not any(losses.values())

    return {
        "scope": [
            "net_table",
            "tracks",
            "recovered_pads",
            "copper_regions",
            "recovered_slots",
        ],
        "roundtrip_equal": roundtrip_equal,
        "source_connectivity_complete": source_connectivity_complete,
        "source_equivalent": bool(roundtrip_equal and source_connectivity_complete),
        "nets": nets,
        "tracks": tracks,
        "pads": pads,
        "regions": regions,
        "slots": slots,
        "losses": losses,
        "issues": issues,
    }


def validate_kicad_connectivity_roundtrip(board, path, export_report):
    path = Path(path)
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    return compare_kicad_connectivity(board, readback, export_report)
