from __future__ import annotations

from math import isfinite

from ..ids import stable_id
from ..models import BoardModel
from .item import ReviewItem
from .queue import ReviewQueue


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
    include_diagnostics: bool = True,
) -> ReviewQueue:
    """Build a deterministic review queue from unresolved reconstruction state.

    Confidence thresholds are opt-in. With no thresholds supplied, the adapter
    surfaces explicit unresolved state already present in the model plus any
    supplied validation findings.
    """

    net_threshold = _review_threshold("net_confidence_below", net_confidence_below)
    component_threshold = _review_threshold(
        "component_confidence_below", component_confidence_below
    )
    queue = ReviewQueue()

    if validation is not None:
        object_index = board.object_index()
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
