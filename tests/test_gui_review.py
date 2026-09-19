import pytest

from photonx_eda_pcb.gui.review import collect_review_items
from photonx_eda_pcb.mechanical_features.model import SlotFeature
from photonx_eda_pcb.models import BoardModel, ComponentHypothesis, DrillHit, NetGroup, PadCandidate, ParseDiagnostic, Point
from photonx_eda_pcb.validation import ValidationIssue, ValidationReport


def make_board():
    pad = PadCandidate("pad-1", Point(1.0, 2.0), 1.0, 1.0, "circle", "F.Cu")
    return BoardModel(
        pads=[pad],
        drills=[DrillHit("drill-1", Point(1.0, 2.0), 0.4, plating="unknown")],
        slots=[SlotFeature("slot-1", (0.0, 0.0), (1.0, 0.0), 0.5)],
        nets=[NetGroup("net-1", ["pad-1"], 0.55)],
        components=[ComponentHypothesis("cmp-1", ["pad-1"], "unresolved_pad", 0.15, ["no nearby pad partner"])],
        diagnostics=[ParseDiagnostic("warning", "TEST_DIAGNOSTIC", "test diagnostic", "sample.gbr", 12)],
    )


def test_review_queue_aggregates_validation_and_uncertainty():
    board = make_board()
    report = ValidationReport([ValidationIssue("error", "TEST_ERROR", "test issue", ("pad-1",))])
    items = collect_review_items(board, report)
    by_code = {item.code: item for item in items}

    assert items[0].code == "TEST_ERROR"
    assert by_code["TEST_ERROR"].object_id == "pad-1"
    assert by_code["UNRESOLVED_COMPONENT"].object_id == "pad-1"
    assert by_code["LOW_NET_CONFIDENCE"].object_id == "pad-1"
    assert by_code["DRILL_PLATING_UNKNOWN"].object_id == "drill-1"
    assert by_code["SLOT_PLATING_UNKNOWN"].object_id == "slot-1"
    assert by_code["TEST_DIAGNOSTIC"].object_id is None
    assert "sample.gbr:12" in by_code["TEST_DIAGNOSTIC"].message


def test_review_queue_respects_confidence_threshold():
    board = make_board()
    board.nets[0].confidence = 0.8
    board.components[0].kind = "resistor_like"
    board.components[0].confidence = 0.8
    codes = {item.code for item in collect_review_items(board, ValidationReport())}
    assert "LOW_NET_CONFIDENCE" not in codes
    assert "LOW_COMPONENT_CONFIDENCE" not in codes


@pytest.mark.parametrize("threshold", [-0.01, 1.01])
def test_review_queue_rejects_invalid_threshold(threshold):
    with pytest.raises(ValueError, match="low_confidence_threshold"):
        collect_review_items(make_board(), ValidationReport(), low_confidence_threshold=threshold)
