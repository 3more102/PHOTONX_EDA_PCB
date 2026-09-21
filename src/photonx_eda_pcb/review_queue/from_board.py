from __future__ import annotations

from math import isfinite

from ..drc.clearance import check_unresolved_clearance
from ..drc.model import DrcConfig
from ..ids import stable_id
from ..models import BoardModel
from .item import ReviewItem
from .queue import ReviewQueue
from .route_evidence import build_route_evidence_rows
from .via_evidence import build_via_evidence_rows


def _review_threshold(name: str, value: float | None) -> float | None:
    if value is None:
        return None
    numeric = float(value)
    if not isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")
    return numeric


def build_board_review_queue(
    board: BoardModel,
    *,
    validation=None,
    net_confidence_below: float | None = None,
    component_confidence_below: float | None = None,
    include_unknown_plating: bool = True,
    include_via_evidence: bool = True,
    include_route_evidence: bool = True,
    include_unresolved_clearance: bool = True,
    include_diagnostics: bool = True,
    drc_config: DrcConfig | None = None,
) -> ReviewQueue:
    """Build a deterministic review queue from unresolved reconstruction state.

    Confidence thresholds are opt-in. With no thresholds supplied, the adapter
    surfaces explicit unresolved state already present in the model plus any
    supplied validation findings. Close copper pairs with unresolved net
    identity are review warnings, never fabricated cross-net DRC errors.
    """

    net_threshold = _review_threshold("net_confidence_below", net_confidence_below)
    component_threshold = _review_threshold(
        "component_confidence_below", component_confidence_below
    )
    queue = ReviewQueue()
    object_index = board.object_index()

    if validation is not None:
        for issue in sorted(
            getattr(validation, "issues", ()),
            key=lambda item: (
                item.severity,
                item.code,
                item.message,
                tuple(item.object_ids),
            ),
        ):
            selectable = next(
                (object_id for object_id in issue.object_ids if object_id in object_index),
                None,
            )
            target = selectable or f"validation:{issue.code}"
            queue.add(
                ReviewItem(
                    stable_id(
                        "review",
                        "validation",
                        issue.severity,
                        issue.code,
                        issue.message,
                        tuple(issue.object_ids),
                    ),
                    "validation",
                    target,
                    f"{issue.severity}: {issue.code}: {issue.message}",
                    0.0,
                    metadata={
                        "confidence_available": False,
                        "severity": issue.severity,
                        "code": issue.code,
                        "object_ids": tuple(issue.object_ids),
                        "selectable_object_id": selectable,
                    },
                )
            )

    if include_unresolved_clearance:
        cfg = drc_config or DrcConfig()
        for issue in check_unresolved_clearance(board, cfg):
            selectable = next(
                (object_id for object_id in issue.object_ids if object_id in object_index),
                None,
            )
            target = selectable or f"clearance:{':'.join(issue.object_ids)}"
            queue.add(
                ReviewItem(
                    stable_id(
                        "review",
                        "clearance",
                        issue.code,
                        tuple(issue.object_ids),
                        issue.message,
                    ),
                    "clearance",
                    target,
                    f"{issue.severity}: {issue.code}: {issue.message}",
                    0.0,
                    metadata={
                        "confidence_available": False,
                        "severity": issue.severity,
                        "code": issue.code,
                        "object_ids": tuple(issue.object_ids),
                        "selectable_object_id": selectable,
                        "minimum_clearance_mm": cfg.min_clearance_mm,
                    },
                )
            )

    if include_unknown_plating:
        for drill in sorted(board.drills, key=lambda item: item.id):
            if drill.plating != "unknown":
                continue
            queue.add(
                ReviewItem(
                    stable_id("review", "drill-plating", drill.id),
                    "drill",
                    drill.id,
                    "drill plating unresolved",
                    0.0,
                    metadata={
                        "confidence_available": False,
                        "plating": drill.plating,
                        "tool": drill.tool,
                        "diameter": drill.diameter,
                    },
                )
            )

        for slot in sorted(getattr(board, "slots", ()), key=lambda item: item.id):
            if str(slot.plated).lower() != "unknown":
                continue
            queue.add(
                ReviewItem(
                    stable_id("review", "slot-plating", slot.id),
                    "slot",
                    slot.id,
                    "slot plating unresolved",
                    0.0,
                    metadata={
                        "confidence_available": False,
                        "plating": slot.plated,
                        "tool": getattr(slot, "tool", None),
                        "width_mm": slot.width_mm,
                    },
                )
            )

    if include_via_evidence:
        for row in build_via_evidence_rows(board):
            if row["status"] == "exportable":
                continue
            drill_id = str(row["drill_id"])
            selectable = drill_id if drill_id in object_index else None
            confidence = row["confidence"]
            queue.add(
                ReviewItem(
                    stable_id(
                        "review",
                        "via-span",
                        row["id"],
                        row["status"],
                        row["export_code"],
                        row["reason"],
                    ),
                    "via_span",
                    drill_id,
                    row["reason"],
                    float(confidence) if confidence is not None else 0.0,
                    metadata={
                        "confidence_available": confidence is not None,
                        "status": row["status"],
                        "plating": row["plating"],
                        "layer_span": row["layers"],
                        "net": row["net"],
                        "net_id": row["net_id"],
                        "pad_ids": tuple(row["pad_ids"]),
                        "export_code": row["export_code"],
                        "selectable_object_id": selectable,
                    },
                )
            )


    if include_route_evidence:
        for row in build_route_evidence_rows(board):
            if row["status"] == "exportable":
                continue
            route_id = str(row["route_id"])
            selectable = route_id if route_id in object_index else None
            queue.add(
                ReviewItem(
                    stable_id(
                        "review",
                        "route-evidence",
                        row["id"],
                        row["status"],
                        row["export_code"],
                        row["reason"],
                    ),
                    "route_evidence",
                    route_id,
                    row["reason"],
                    0.0,
                    metadata={
                        "confidence_available": False,
                        "status": row["status"],
                        "plating": row["plating"],
                        "layer_span": row["span"],
                        "span_proven": row["span_proven"],
                        "x2_kind": row["x2_kind"],
                        "width_mm": row["width_mm"],
                        "segments": row["segments"],
                        "net": row["net"],
                        "net_id": row["net_id"],
                        "export_kind": row["export_kind"],
                        "export_code": row["export_code"],
                        "selectable_object_id": selectable,
                    },
                )
            )

    for net in sorted(board.nets, key=lambda item: item.id):
        reasons: list[str] = []
        if net.label is None:
            reasons.append("physical net label unresolved")
        if net_threshold is not None and net.confidence < net_threshold:
            reasons.append(
                f"net confidence {net.confidence:.3f} below review threshold "
                f"{net_threshold:.3f}"
            )
        if not reasons:
            continue
        queue.add(
            ReviewItem(
                stable_id("review", "net", net.id),
                "net",
                net.id,
                "; ".join(reasons),
                net.confidence,
                metadata={
                    "confidence_available": True,
                    "label": net.label,
                    "members": tuple(net.members),
                },
            )
        )

    for component in sorted(board.components, key=lambda item: item.id):
        reasons = []
        if component.reference is None:
            reasons.append("component reference unresolved")
        if (
            component_threshold is not None
            and component.confidence < component_threshold
        ):
            reasons.append(
                f"component confidence {component.confidence:.3f} below review "
                f"threshold {component_threshold:.3f}"
            )
        if not reasons:
            continue
        queue.add(
            ReviewItem(
                stable_id("review", "component", component.id),
                "component",
                component.id,
                "; ".join(reasons),
                component.confidence,
                metadata={
                    "confidence_available": True,
                    "kind": component.kind,
                    "reference": component.reference,
                    "pad_ids": tuple(component.pad_ids),
                    "evidence": tuple(component.evidence),
                },
            )
        )

    if include_diagnostics:
        diagnostics = sorted(
            board.diagnostics,
            key=lambda item: (
                item.severity,
                item.code,
                item.path,
                -1 if item.line is None else item.line,
                item.message,
            ),
        )
        for diagnostic in diagnostics:
            target = (
                f"{diagnostic.path}:{diagnostic.line}"
                if diagnostic.line is not None
                else diagnostic.path
            )
            queue.add(
                ReviewItem(
                    stable_id(
                        "review",
                        "diagnostic",
                        diagnostic.severity,
                        diagnostic.code,
                        diagnostic.path,
                        diagnostic.line,
                        diagnostic.message,
                    ),
                    "diagnostic",
                    target,
                    f"{diagnostic.severity}: {diagnostic.code}: "
                    f"{diagnostic.message}",
                    0.0,
                    metadata={
                        "confidence_available": False,
                        "severity": diagnostic.severity,
                        "code": diagnostic.code,
                        "path": diagnostic.path,
                        "line": diagnostic.line,
                    },
                )
            )

    return queue
