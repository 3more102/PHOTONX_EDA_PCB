from __future__ import annotations

import math

from photonx_eda_pcb.gui.confidence import (
    confidence_band,
    confidence_color,
    net_confidence,
    net_confidence_summary,
    normalize_confidence,
    object_confidence,
    object_review_context,
)
from photonx_eda_pcb.models import BoardModel, NetGroup, PadCandidate, Point, Track


def _board() -> BoardModel:
    return BoardModel(
        tracks=[
            Track(
                id="track-high",
                start=Point(0.0, 0.0),
                end=Point(1.0, 0.0),
                width=0.2,
                layer="F.Cu",
                net_id="net-high",
            ),
            Track(
                id="track-low",
                start=Point(0.0, 1.0),
                end=Point(1.0, 1.0),
                width=0.2,
                layer="F.Cu",
                net_id="net-low",
            ),
        ],
        pads=[
            PadCandidate(
                id="pad-unknown",
                center=Point(2.0, 2.0),
                size_x=1.0,
                size_y=1.0,
                shape="circle",
                layer="F.Cu",
                net_id=None,
            )
        ],
        nets=[
            NetGroup(id="net-high", members=["track-high"], confidence=0.95),
            NetGroup(id="net-medium", members=[], confidence=0.75),
            NetGroup(id="net-low", members=["track-low"], confidence=0.40),
        ],
    )


def test_normalize_confidence_is_bounded_and_rejects_non_finite_values():
    assert normalize_confidence(-0.2) == 0.0
    assert normalize_confidence(1.2) == 1.0
    assert normalize_confidence("0.8") == 0.8
    assert normalize_confidence(None) is None
    assert normalize_confidence(math.nan) is None
    assert normalize_confidence(math.inf) is None


def test_confidence_bands_have_explicit_unknown_state():
    assert confidence_band(0.95) == "high"
    assert confidence_band(0.90) == "high"
    assert confidence_band(0.70) == "medium"
    assert confidence_band(0.69) == "low"
    assert confidence_band(None) == "unknown"
    assert confidence_color(None) != confidence_color(0.95)


def test_object_confidence_comes_only_from_existing_physical_net_evidence():
    board = _board()

    assert net_confidence(board, "net-high") == 0.95
    assert object_confidence(board, "track-high") == 0.95
    assert object_confidence(board, "track-low") == 0.40
    assert object_confidence(board, "pad-unknown") is None
    assert object_confidence(board, "missing") is None

    unknown = object_review_context(board, "pad-unknown")
    assert unknown["confidence_source"] == "unknown"
    assert unknown["confidence"] is None
    assert unknown["confidence_band"] == "unknown"


def test_net_confidence_summary_is_deterministic():
    assert net_confidence_summary(_board()) == {
        "high": 1,
        "medium": 1,
        "low": 1,
        "unknown": 0,
    }
