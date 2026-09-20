from __future__ import annotations

from collections import Counter
from math import isfinite

from ..exporters.kicad_policy import proven_via_span_export_plan


def _confidence(value) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        return None
    return numeric


def _layer_span(span: dict) -> str:
    layer_ids = span.get("layer_ids", ())
    if isinstance(layer_ids, (list, tuple)) and layer_ids:
        return " -> ".join(str(layer) for layer in layer_ids)

    start = span.get("from_layer")
    end = span.get("to_layer")
    if start and end:
        return str(start) if start == end else f"{start} -> {end}"
    if start or end:
        return str(start or end)
    return "—"


def _resolved_net(board, pad_ids, exportable=None):
    if exportable is not None:
        net_id = exportable.get("net_id")
        return (str(net_id), str(net_id)) if net_id is not None else (None, "—")

    pad_by_id = {str(pad.id): pad for pad in getattr(board, "pads", ())}
    pads = [pad_by_id.get(str(pad_id)) for pad_id in pad_ids]
    if not pads or any(pad is None for pad in pads):
        return None, "—"

    net_ids = [getattr(pad, "net_id", None) for pad in pads]
    if any(net_id is None for net_id in net_ids):
        return None, "—"

    unique = {str(net_id) for net_id in net_ids}
    if len(unique) == 1:
        net_id = next(iter(unique))
        return net_id, net_id
    return None, "<conflict>"


def build_via_evidence_rows(board) -> list[dict]:
    """Build deterministic review rows for reconstructed via-span evidence.

    The status reuses the KiCad export policy rather than duplicating its
    eligibility rules:
    - exportable: a proven span is exactly representable as a KiCad via;
    - omitted: a proven span is valid evidence but current KiCad semantics
      cannot represent it without guessing;
    - unproven: reconstruction did not prove a plated vertical connection;
    - invalid: via-span metadata itself is contradictory or malformed.
    """

    metadata = getattr(board, "metadata", {}) or {}
    raw_spans = metadata.get("via_spans", ()) if isinstance(metadata, dict) else ()
    if raw_spans is None:
        raw_spans = ()

    exportable, omitted, problems = proven_via_span_export_plan(board)
    exportable_by_id = {
        str(item["drill_id"]): item
        for item in exportable
        if isinstance(item, dict) and item.get("drill_id") is not None
    }
    omitted_by_id = {
        str(drill_id): (str(code), str(message))
        for drill_id, code, message in omitted
    }
    problems_by_id: dict[str, list[str]] = {}
    for object_id, message in problems:
        problems_by_id.setdefault(str(object_id), []).append(str(message))

    if not isinstance(raw_spans, (list, tuple)):
        reason = "; ".join(problems_by_id.get("via_spans", ())) or (
            "via_spans metadata must be a list or tuple"
        )
        return [
            {
                "id": "via-span:metadata",
                "drill_id": "via_spans",
                "status": "invalid",
                "plating": "—",
                "layers": "—",
                "net": "—",
                "net_id": None,
                "confidence": None,
                "pad_ids": (),
                "reason": reason,
                "export_code": None,
            }
        ]

    drill_by_id = {str(drill.id): drill for drill in getattr(board, "drills", ())}
    ids = [
        str(span.get("drill_id"))
        for span in raw_spans
        if isinstance(span, dict)
        and isinstance(span.get("drill_id"), str)
        and span.get("drill_id")
    ]
    duplicate_ids = {drill_id for drill_id, count in Counter(ids).items() if count > 1}

    rows = []
    for index, span in enumerate(raw_spans):
        metadata_id = f"via_spans[{index}]"
        if not isinstance(span, dict):
            reason = "; ".join(problems_by_id.get(metadata_id, ())) or (
                "via-span metadata entry must be a mapping"
            )
            rows.append(
                {
                    "id": f"via-span:{index}:invalid",
                    "drill_id": metadata_id,
                    "status": "invalid",
                    "plating": "—",
                    "layers": "—",
                    "net": "—",
                    "net_id": None,
                    "confidence": None,
                    "pad_ids": (),
                    "reason": reason,
                    "export_code": None,
                }
            )
            continue

        raw_drill_id = span.get("drill_id")
        drill_id = (
            raw_drill_id
            if isinstance(raw_drill_id, str) and raw_drill_id
            else metadata_id
        )
        drill = drill_by_id.get(str(drill_id))
        plating = (
            str(getattr(drill, "plating", "unknown"))
            if drill is not None
            else "missing"
        )

        raw_pad_ids = span.get("pad_ids", ())
        pad_ids = (
            tuple(str(pad_id) for pad_id in raw_pad_ids)
            if isinstance(raw_pad_ids, (list, tuple))
            else ()
        )
        confidence = _confidence(span.get("confidence"))
        proven = span.get("proven")
        export_item = exportable_by_id.get(str(drill_id))
        omission = omitted_by_id.get(str(drill_id))
        specific_problems = [
            *problems_by_id.get(metadata_id, ()),
            *problems_by_id.get(str(drill_id), ()),
        ]

        export_code = None
        if str(drill_id) in duplicate_ids:
            status = "invalid"
            reason = "duplicate via-span drill ID in reconstruction metadata"
        elif specific_problems:
            status = "invalid"
            reason = "; ".join(dict.fromkeys(specific_problems))
        elif not isinstance(proven, bool):
            status = "invalid"
            reason = "via-span proven flag must be boolean"
        elif not proven:
            status = "unproven"
            if span.get("from_layer") and span.get("to_layer"):
                reason = (
                    "copper-layer contact is reconstructed, but plating/span "
                    "evidence does not prove a vertical electrical via"
                )
            else:
                reason = "no proven multilayer plated via span"
        elif export_item is not None:
            status = "exportable"
            reason = "proven span is exactly representable by current KiCad via policy"
        elif omission is not None:
            status = "omitted"
            export_code, reason = omission
        else:
            status = "invalid"
            reason = "proven via span has no deterministic export-plan classification"

        net_id, net_text = _resolved_net(board, pad_ids, export_item)
        rows.append(
            {
                "id": f"via-span:{index}:{drill_id}",
                "drill_id": str(drill_id),
                "status": status,
                "plating": plating,
                "layers": _layer_span(span),
                "net": net_text,
                "net_id": net_id,
                "confidence": confidence,
                "pad_ids": pad_ids,
                "reason": reason,
                "export_code": export_code,
            }
        )

    return rows
