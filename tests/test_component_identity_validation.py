from photonx_eda_pcb.checks.components import check_components
from photonx_eda_pcb.models import BoardModel, ComponentHypothesis, PadCandidate, Point
from photonx_eda_pcb.validation import validate_board
from photonx_eda_pcb.validation_rules.component_rules import valid_component_references


def _pad() -> PadCandidate:
    return PadCandidate("P1", Point(0.0, 0.0), 1.0, 1.0, "C", "F.Cu")


def _codes(board: BoardModel) -> tuple[set[str], set[str], set[str]]:
    return (
        {issue.code for issue in validate_board(board).issues},
        {issue.code for issue in check_components(board)},
        {issue.code for issue in valid_component_references(board)},
    )


def test_duplicate_component_ids_are_rejected_consistently():
    board = BoardModel(
        pads=[_pad()],
        components=[
            ComponentHypothesis("C1", ["P1"], "candidate", 0.8, []),
            ComponentHypothesis("C1", ["P1"], "candidate", 0.7, []),
        ],
    )

    for codes in _codes(board):
        assert "DUPLICATE_COMPONENT_ID" in codes


def test_duplicate_pad_references_inside_component_are_rejected_consistently():
    board = BoardModel(
        pads=[_pad()],
        components=[
            ComponentHypothesis("C1", ["P1", "P1"], "candidate", 0.8, []),
        ],
    )

    for codes in _codes(board):
        assert "COMPONENT_PAD_DUPLICATE" in codes
