from __future__ import annotations

from dataclasses import dataclass

from ..models import BoardModel
from ..validation import ValidationReport


@dataclass(frozen=True)
class ReviewItem:
    severity: str
    category: str
    code: str
    message: str
    object_id: str | None = None


def _selectable_object_id(board: BoardModel, object_ids) -> str | None:
    index = board.object_index()
    for object_id in object_ids:
        if object_id in index:
            return object_id
    return None


def collect_review_items(
    board: BoardModel,
    validation: ValidationReport,
    *,
    low_confidence_threshold: float = 0.7,
) -> list[ReviewItem]:
    """Build a deterministic evidence-review queue without changing model state."""
    threshold = float(low_confidence_threshold)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("low_confidence_threshold must be between 0 and 1")

    items: list[ReviewItem] = []

    for issue in validation.issues:
        items.append(
            ReviewItem(
                issue.severity,
                "validation",
                issue.code,
                issue.message,
                _selectable_object_id(board, issue.object_ids),
            )
        )

    for diagnostic in board.diagnostics:
        location = diagnostic.path
        if diagnostic.line is not None:
            location = f"{location}:{diagnostic.line}"
        items.append(
            ReviewItem(
                diagnostic.severity,
                "parser",
                diagnostic.code,
                f"{diagnostic.message} ({location})",
            )
        )

    for net in board.nets:
        confidence = float(net.confidence)
        if confidence < threshold:
            items.append(
                ReviewItem(
                    "review",
                    "net",
                    "LOW_NET_CONFIDENCE",
                    f"{net.id} confidence={confidence:.3f}",
                    _selectable_object_id(board, net.members),
                )
            )

    for component in board.components:
        confidence = float(component.confidence)
        unresolved = str(component.kind).startswith("unresolved")
        if unresolved:
            code = "UNRESOLVED_COMPONENT"
            severity = "warning"
        elif confidence < threshold:
            code = "LOW_COMPONENT_CONFIDENCE"
            severity = "review"
        else:
            continue
        evidence = "; ".join(str(item) for item in component.evidence) or "no evidence detail"
        items.append(
            ReviewItem(
                severity,
                "component",
                code,
                f"{component.id} kind={component.kind} confidence={confidence:.3f}; {evidence}",
                _selectable_object_id(board, component.pad_ids),
            )
        )

    for drill in board.drills:
        if str(drill.plating).lower() == "unknown":
            items.append(
                ReviewItem(
                    "review",
                    "drill",
                    "DRILL_PLATING_UNKNOWN",
                    f"{drill.id} plating remains unknown",
                    drill.id,
                )
            )

    for slot in getattr(board, "slots", ()):
        if str(slot.plated).lower() == "unknown":
            items.append(
                ReviewItem(
                    "review",
                    "slot",
                    "SLOT_PLATING_UNKNOWN",
                    f"{slot.id} plating remains unknown",
                    slot.id,
                )
            )

    priority = {"error": 0, "warning": 1, "review": 2, "info": 3}
    return sorted(
        items,
        key=lambda item: (
            priority.get(item.severity, 4),
            item.category,
            item.code,
            item.object_id or "",
            item.message,
        ),
    )
