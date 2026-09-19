import pytest

from photonx_eda_pcb.models import (
    BoardModel,
    ComponentHypothesis,
    DrillHit,
    NetGroup,
    ParseDiagnostic,
    Point,
)
from photonx_eda_pcb.review_queue import build_board_review_queue


def _board() -> BoardModel:
    return BoardModel(
        drills=[
            DrillHit("D1", Point(0, 0), 0.4, "unknown", "T01"),
            DrillHit("D2", Point(1, 0), 0.4, "plated", "T02"),
        ],
        nets=[
            NetGroup("N1", ["P1"], 0.90),
            NetGroup("N2", ["P2"], 0.80, label="GND"),
        ],
        components=[
            ComponentHypothesis("C1", ["P1"], "TWO_PIN_THT", 0.70, ["geometry"]),
            ComponentHypothesis(
                "C2", ["P2"], "TWO_PIN_THT", 0.60, ["geometry"], reference="R1"
            ),
        ],
        diagnostics=[
            ParseDiagnostic(
                "warning",
                "UNSUPPORTED_HINT",
                "ignored non-geometric hint",
                "top.gbr",
                12,
            )
        ],
    )


def test_board_review_queue_surfaces_explicit_unresolved_state_deterministically():
    first = build_board_review_queue(_board())
    second = build_board_review_queue(_board())

    items = first.open_items()
    targets = {(item.kind, item.target_id) for item in items}

    assert ("drill", "D1") in targets
    assert ("net", "N1") in targets
    assert ("component", "C1") in targets
    assert ("diagnostic", "top.gbr:12") in targets
    assert ("drill", "D2") not in targets
    assert ("net", "N2") not in targets
    assert ("component", "C2") not in targets
    assert [item.id for item in items] == [item.id for item in second.open_items()]

    diagnostic = next(item for item in items if item.kind == "diagnostic")
    assert diagnostic.metadata["confidence_available"] is False


def test_confidence_review_thresholds_are_explicit_and_opt_in():
    board = _board()

    default_targets = {
        (item.kind, item.target_id) for item in build_board_review_queue(board).all()
    }
    assert ("net", "N2") not in default_targets
    assert ("component", "C2") not in default_targets

    threshold_targets = {
        (item.kind, item.target_id)
        for item in build_board_review_queue(
            board,
            net_confidence_below=0.85,
            component_confidence_below=0.65,
        ).all()
    }
    assert ("net", "N2") in threshold_targets
    assert ("component", "C2") in threshold_targets


@pytest.mark.parametrize("value", [-0.01, 1.01, float("inf"), float("nan")])
def test_review_thresholds_reject_invalid_values(value):
    with pytest.raises(ValueError):
        build_board_review_queue(_board(), net_confidence_below=value)
