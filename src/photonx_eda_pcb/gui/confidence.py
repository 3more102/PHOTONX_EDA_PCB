from __future__ import annotations

import math

from ..models import BoardModel


CONFIDENCE_COLORS = {
    "high": "#188038",
    "medium": "#e37400",
    "low": "#c5221f",
    "unknown": "#5f6368",
}


def normalize_confidence(value: object) -> float | None:
    """Return a finite confidence clamped to [0, 1], or None if unknown."""
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(confidence):
        return None
    return min(1.0, max(0.0, confidence))


def confidence_band(confidence: object) -> str:
    value = normalize_confidence(confidence)
    if value is None:
        return "unknown"
    if value >= 0.90:
        return "high"
    if value >= 0.70:
        return "medium"
    return "low"


def confidence_color(confidence: object) -> str:
    return CONFIDENCE_COLORS[confidence_band(confidence)]


def net_confidence(board: BoardModel, net_id: str | None) -> float | None:
    if not net_id:
        return None
    for net in board.nets:
        if net.id == net_id:
            return normalize_confidence(net.confidence)
    return None


def object_confidence(board: BoardModel, object_id: str) -> float | None:
    obj = board.object_index().get(object_id)
    if obj is None:
        return None
    return net_confidence(board, getattr(obj, "net_id", None))


def object_review_context(board: BoardModel, object_id: str) -> dict[str, object]:
    obj = board.object_index().get(object_id)
    if obj is None:
        return {
            "confidence_source": "unknown",
            "confidence": None,
            "confidence_band": "unknown",
        }

    net_id = getattr(obj, "net_id", None)
    confidence = net_confidence(board, net_id)
    return {
        "confidence_source": "physical_net" if net_id else "unknown",
        "net_id": net_id,
        "confidence": confidence,
        "confidence_band": confidence_band(confidence),
    }


def net_confidence_summary(board: BoardModel) -> dict[str, int]:
    summary = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    for net in board.nets:
        summary[confidence_band(net.confidence)] += 1
    return summary
