from __future__ import annotations

import json
from collections import Counter
from math import cos, radians, sin
from pathlib import Path

from ..kicad_reader import read_kicad_board_text


_ROUND_DIGITS = 6
_RECOVERED_PAD_FOOTPRINT = "PHOTONX:RecoveredPad"


def _r(value):
    return round(float(value), _ROUND_DIGITS)


def _point(value):
    if value is None or len(value) < 2:
        raise ValueError("point must contain x/y coordinates")
    return (_r(value[0]), _r(value[1]))


def _net_table_from_board(board):
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


def _observed_net_lookup(readback):
    lookup = {}
    duplicates = []
    for row in readback.get("nets", ()):
        code = int(row["code"])
        name = str(row["name"])
        if code in lookup and lookup[code] != name:
            duplicates.append(code)
        lookup[code] = name
    return lookup, sorted(set(duplicates))


def _binding_from_code(code, lookup, issues, object_kind):
    if code in (None, 0):
        return {"code": 0, "name": ""}
    code = int(code)
    if code not in lookup:
        issues.append(
            {
                "code": "KICAD_ROUNDTRIP_UNKNOWN_NET_CODE",
                "object_kind": object_kind,
                "net_code": code,
            }
        )
        return {"code": code, "name": None}
    return {"code": code, "name": str(lookup[code])}


def _track_item(start, end, width, layer, binding):
    a, b = sorted((_point(start), _point(end)))
    return {
        "start": list(a),
        "end": list(b),
        "width": _r(width),
        "layer": str(layer),
        "net": binding,
    }


def _pad_item(center, size, drill, binding):
    return {
        "center": list(_point(center)),
        "size": [_r(size[0]), _r(size[1])],
        "drill": None if drill is None else _r(drill),
        "net": binding,
    }


def _stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _compare_multiset(expected, observed):
    expected_keys = [_stable(item) for item in expected]
    observed_keys = [_stable(item) for item in observed]
    ec = Counter(expected_keys)
    oc = Counter(observed_keys)

    missing = []
    for key, count in sorted((ec - oc).items()):
        missing.extend(json.loads(key) for _ in range(count))

    unexpected = []
    for key, count in sorted((oc - ec).items()):
        unexpected.extend(json.loads(key) for _ in range(count))

    return {
        "equal": ec == oc,
        "expected_count": len(expected),
        "observed_count": len(observed),
        "missing": missing,
        "unexpected": unexpected,
    }


def _reported_track_sets(board, export_report, issues):
    source_ids = {track.id for track in board.tracks}
    if export_report is None:
        exported = {
            track.id
            for track in board.tracks
            if _source_net_binding(board, track.net_id) is not None
        }
        skipped = source_ids - exported
        return exported, skipped

    exported = set(getattr(export_report, "exported_track_ids", ()))
    skipped = set(getattr(export_report, "skipped_track_ids", ()))

    overlap = sorted(exported & skipped)
    if overlap:
        issues.append(
            {
                "code": "KICAD_ROUNDTRIP_TRACK_REPORT_OVERLAP",
                "track_ids": overlap,
            }
        )

    unknown = sorted((exported | skipped) - source_ids)
    if unknown:
        issues.append(
            {
                "code": "KICAD_ROUNDTRIP_TRACK_REPORT_UNKNOWN_IDS",
                "track_ids": unknown,
            }
        )

    undecided = sorted(source_ids - exported - skipped)
    if undecided:
        issues.append(
            {
                "code": "KICAD_ROUNDTRIP_TRACK_REPORT_MISSING_IDS",
                "track_ids": undecided,
            }
        )

    return exported & source_ids, skipped & source_ids


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
            )
        )
    return out


def _observed_tracks(readback, net_lookup, issues):
    out = []
    for index, segment in enumerate(readback.get("segments", ())):
        try:
            binding = _binding_from_code(
                segment.get("net"), net_lookup, issues, "segment"
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
    out = []
    unresolved = []
    for pad in board.pads:
        binding = _source_net_binding(board, pad.net_id)
        if binding is None:
            unresolved.append(pad.id)
            binding = {"code": 0, "name": ""}
        out.append(
            _pad_item(
                (pad.center.x, pad.center.y),
                (pad.size_x, pad.size_y),
                pad.drill,
                binding,
            )
        )
    return out, sorted(unresolved)


def _global_pad_center(footprint, pad):
    fx, fy = footprint.get("at", (0.0, 0.0))
    px, py = pad.get("at", (0.0, 0.0))
    theta = radians(float(footprint.get("angle", 0.0) or 0.0))
    return (
        float(fx) + float(px) * cos(theta) - float(py) * sin(theta),
        float(fy) + float(px) * sin(theta) + float(py) * cos(theta),
    )


def _observed_pads(readback, net_lookup, issues):
    out = []
    for fp_index, footprint in enumerate(readback.get("footprints", ())):
        if footprint.get("name") != _RECOVERED_PAD_FOOTPRINT:
            continue
        for pad_index, pad in enumerate(footprint.get("pads", ())):
            try:
                size = pad.get("size")
                if size is None:
                    raise ValueError("pad size missing")
                binding = _binding_from_code(
                    pad.get("net"), net_lookup, issues, "pad"
                )
                out.append(
                    _pad_item(
                        _global_pad_center(footprint, pad),
                        size,
                        pad.get("drill"),
                        binding,
                    )
                )
            except (TypeError, ValueError, IndexError, KeyError) as exc:
                issues.append(
                    {
                        "code": "KICAD_ROUNDTRIP_INVALID_PAD",
                        "footprint_index": fp_index,
                        "pad_index": pad_index,
                        "detail": str(exc),
                    }
                )
    return out


def compare_kicad_connectivity(board, readback, export_report=None):
    """Compare exported KiCad connectivity against the source board model.

    The comparison is deliberately limited to net-table identity, exported
    track-segment bindings, and recovered-pad bindings. Copper-region/zone and
    plated-slot connectivity are outside this validator's current scope.

    ``roundtrip_equal`` means the re-read KiCad file matches the export policy.
    ``source_equivalent`` additionally requires that no source connectivity was
    intentionally lost because an unresolved track/pad net could not be
    represented faithfully.
    """

    issues = []
    net_lookup, duplicate_codes = _observed_net_lookup(readback)
    if duplicate_codes:
        issues.append(
            {
                "code": "KICAD_ROUNDTRIP_DUPLICATE_NET_CODES",
                "net_codes": duplicate_codes,
            }
        )

    expected_nets = _net_table_from_board(board)
    observed_nets = [
        {"code": int(row["code"]), "name": str(row["name"])}
        for row in readback.get("nets", ())
    ]
    nets = _compare_multiset(expected_nets, observed_nets)

    exported_track_ids, skipped_track_ids = _reported_track_sets(
        board, export_report, issues
    )
    expected_tracks = _expected_tracks(board, exported_track_ids, issues)
    observed_tracks = _observed_tracks(readback, net_lookup, issues)
    tracks = _compare_multiset(expected_tracks, observed_tracks)

    expected_pads, unresolved_pad_ids = _expected_pads(board)
    observed_pads = _observed_pads(readback, net_lookup, issues)
    pads = _compare_multiset(expected_pads, observed_pads)

    roundtrip_equal = bool(
        nets["equal"] and tracks["equal"] and pads["equal"] and not issues
    )
    losses = {
        "skipped_track_ids": sorted(skipped_track_ids),
        "unresolved_pad_net_ids": unresolved_pad_ids,
    }
    source_connectivity_complete = not any(losses.values())

    return {
        "scope": ["net_table", "tracks", "recovered_pads"],
        "roundtrip_equal": roundtrip_equal,
        "source_connectivity_complete": source_connectivity_complete,
        "source_equivalent": bool(roundtrip_equal and source_connectivity_complete),
        "nets": nets,
        "tracks": tracks,
        "pads": pads,
        "losses": losses,
        "issues": issues,
    }


def validate_kicad_connectivity_roundtrip(board, path, export_report=None):
    path = Path(path)
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    return compare_kicad_connectivity(board, readback, export_report)
