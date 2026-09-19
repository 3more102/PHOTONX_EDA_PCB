import pytest

from photonx_eda_pcb.mechanical_features.model import SlotFeature
from photonx_eda_pcb.models import (
    BoardModel,
    ComponentHypothesis,
    DrillHit,
    NetGroup,
    ParseDiagnostic,
    Point,
)
from photonx_eda_pcb.review_queue import build_board_review_queue
from photonx_eda_pcb.validation import ValidationIssue, ValidationReport


def _board() -> BoardModel:
    return BoardModel(
        drills=[
            DrillHit("D1", Point(0, 0), 0.4, "unknown", "T01"),
            DrillHit("D2", Point(1, 0), 0.4, "plated", "T02"),
        ],
        slots=[
            SlotFeature("S1", (0, 0), (1, 0), 0.5, "unknown"),
            SlotFeature("S2", (0, 1), (1, 1), 0.5, "plated"),
        ],
        nets=[
            NetGroup("N1", ["D1"], 0.90),
            NetGroup("N2", ["D2"], 0.80, label="GND"),
        ],
        components=[
            ComponentHypothesis("C1", ["D1"], "TWO_PIN_THT", 0.70, ["geometry"]),
            ComponentHypothesis(
                "C2", ["D2"], "TWO_PIN_THT", 0.60, ["geometry"], reference="R1"
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
    assert ("slot", "S1") in targets
    assert ("net", "N1") in targets
    assert ("component", "C1") in targets
    assert ("diagnostic", "top.gbr:12") in targets
    assert ("drill", "D2") not in targets
    assert ("slot", "S2") not in targets
    assert ("net", "N2") not in targets
    assert ("component", "C2") not in targets
    assert [item.id for item in items] == [item.id for item in second.open_items()]

    diagnostic = next(item for item in items if item.kind == "diagnostic")
    assert diagnostic.metadata["confidence_available"] is False


def test_validation_findings_are_included_without_inventing_confidence():
    report = ValidationReport(
        [ValidationIssue("error", "TEST_ERROR", "test issue", ("D1",))]
    )

    queue = build_board_review_queue(_board(), validation=report)
    item = next(item for item in queue.all() if item.kind == "validation")

    assert item.target_id == "D1"
    assert item.metadata["selectable_object_id"] == "D1"
    assert item.metadata["confidence_available"] is False
    assert item.metadata["code"] == "TEST_ERROR"


def test_validation_without_selectable_object_remains_reviewable():
    report = ValidationReport(
        [ValidationIssue("warning", "BOARD_WARNING", "board-level issue")]
    )

    queue = build_board_review_queue(_board(), validation=report)
    item = next(item for item in queue.all() if item.kind == "validation")

    assert item.target_id == "validation:BOARD_WARNING"
    assert item.metadata["selectable_object_id"] is None


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
