from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from ..exporters.kicad_policy import proven_via_span_export_plan


@dataclass(frozen=True)
class ViaReviewDescriptor:
    drill_id: str
    x: float
    y: float
    diameter: float
    plating: str
    from_layer: str | None
    to_layer: str | None
    layer_ids: tuple[str, ...]
    pad_ids: tuple[str, ...]
    confidence: float | None
    proven: bool
    evidence: tuple[str, ...]
    status: str
    export_code: str | None = None
    export_message: str | None = None
    net_id: str | None = None


def _finite_float(value) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


def _common_net_id(board, pad_ids: tuple[str, ...]) -> str | None:
    pads = {str(pad.id): pad for pad in getattr(board, "pads", ())}
    if any(pad_id not in pads for pad_id in pad_ids):
        return None
    nets = {
        getattr(pads[pad_id], "net_id", None)
        for pad_id in pad_ids
    }
    if len(nets) != 1:
        return None
    net_id = next(iter(nets))
    return str(net_id) if net_id is not None else None


def build_via_review_descriptors(board) -> tuple[ViaReviewDescriptor, ...]:
    """Build model-backed via review rows without inventing missing evidence."""

    metadata = getattr(board, "metadata", {}) or {}
    if not isinstance(metadata, dict):
        return ()

    raw_spans = metadata.get("via_spans", ())
    if not isinstance(raw_spans, (list, tuple)):
        return ()

    exportable, omitted, problems = proven_via_span_export_plan(board)
    exportable_by_id = {item["drill_id"]: item for item in exportable}
    omitted_by_id = {
        drill_id: (code, message)
        for drill_id, code, message in omitted
    }
    problem_by_id = {
        str(object_id): message
        for object_id, message in problems
    }
    drills = {
        str(drill.id): drill
        for drill in getattr(board, "drills", ())
    }

    rows: list[ViaReviewDescriptor] = []
    for index, span in enumerate(raw_spans):
        if not isinstance(span, dict):
            continue

        drill_id = span.get("drill_id")
        if not isinstance(drill_id, str) or not drill_id:
            continue

        drill = drills.get(drill_id)
        if drill is None:
            continue

        x = _finite_float(getattr(getattr(drill, "center", None), "x", None))
        y = _finite_float(getattr(getattr(drill, "center", None), "y", None))
        diameter = _finite_float(getattr(drill, "diameter", None))
        if x is None or y is None or diameter is None or diameter <= 0:
            continue

        pad_ids_raw = span.get("pad_ids", ())
        pad_ids = (
            tuple(str(item) for item in pad_ids_raw)
            if isinstance(pad_ids_raw, (list, tuple))
            else ()
        )
        layer_ids_raw = span.get("layer_ids", ())
        layer_ids = (
            tuple(str(item) for item in layer_ids_raw)
            if isinstance(layer_ids_raw, (list, tuple))
            else ()
        )
        evidence_raw = span.get("evidence", ())
        evidence = (
            tuple(str(item) for item in evidence_raw)
            if isinstance(evidence_raw, (list, tuple))
            else ()
        )

        proven = span.get("proven") is True
        confidence = _finite_float(span.get("confidence"))
        from_layer = span.get("from_layer")
        to_layer = span.get("to_layer")
        from_layer = str(from_layer) if isinstance(from_layer, str) and from_layer else None
        to_layer = str(to_layer) if isinstance(to_layer, str) and to_layer else None

        export_code = None
        export_message = None
        net_id = _common_net_id(board, pad_ids)

        if not proven:
            status = "unproven"
        elif drill_id in exportable_by_id:
            status = "exportable"
            net_id = str(exportable_by_id[drill_id]["net_id"])
        elif drill_id in omitted_by_id:
            status = "omitted"
            export_code, export_message = omitted_by_id[drill_id]
        else:
            status = "invalid"
            export_code = "KICAD_PROVEN_VIA_METADATA_INVALID"
            export_message = (
                problem_by_id.get(drill_id)
                or problem_by_id.get(f"via_spans[{index}]")
                or "proven via metadata failed conservative export planning"
            )

        rows.append(
            ViaReviewDescriptor(
                drill_id=drill_id,
                x=x,
                y=y,
                diameter=diameter,
                plating=str(getattr(drill, "plating", "unknown")),
                from_layer=from_layer,
                to_layer=to_layer,
                layer_ids=layer_ids,
                pad_ids=pad_ids,
                confidence=confidence,
                proven=proven,
                evidence=evidence,
                status=status,
                export_code=export_code,
                export_message=export_message,
                net_id=net_id,
            )
        )

    rows.sort(key=lambda row: row.drill_id)
    return tuple(rows)


def via_review_descriptor(board, drill_id: str) -> ViaReviewDescriptor | None:
    for row in build_via_review_descriptors(board):
        if row.drill_id == drill_id:
            return row
    return None


def via_review_summary(board) -> dict[str, int]:
    counts = {
        "exportable": 0,
        "omitted": 0,
        "unproven": 0,
        "invalid": 0,
    }
    for row in build_via_review_descriptors(board):
        counts[row.status] = counts.get(row.status, 0) + 1
    return counts
