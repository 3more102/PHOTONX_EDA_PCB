import pytest

from photonx_eda_pcb.models import BoardModel, OutlineSegment, Point
from photonx_eda_pcb.validation import validate_board


def _segment(segment_id, start, end):
    return OutlineSegment(segment_id, Point(*start), Point(*end))


@pytest.mark.parametrize(
    "tolerance",
    [0, -0.01, float("nan"), float("inf"), float("-inf"), True, None, "bad"],
)
def test_outline_tolerance_must_be_positive_and_finite(tolerance):
    with pytest.raises(ValueError, match="positive finite"):
        validate_board(BoardModel(), outline_tolerance_mm=tolerance)


@pytest.mark.parametrize("bad_coordinate", [float("nan"), float("inf"), float("-inf"), "bad", None])
def test_non_finite_or_non_numeric_outline_coordinate_is_reported(bad_coordinate):
    board = BoardModel(
        outline=[
            OutlineSegment(
                "EDGE_BAD",
                Point(bad_coordinate, 0.0),
                Point(1.0, 0.0),
            )
        ]
    )

    report = validate_board(board)

    assert not report.ok
    issue = next(i for i in report.errors if i.code == "OUTLINE_COORDINATE_INVALID")
    assert issue.object_ids == ("EDGE_BAD",)
    assert not any(i.code == "OUTLINE_NOT_CLOSED" for i in report.issues)


def test_zero_length_outline_segment_is_an_error():
    board = BoardModel(
        outline=[_segment("EDGE_ZERO", (1.0, 2.0), (1.0, 2.0))]
    )

    report = validate_board(board)

    assert not report.ok
    assert any(i.code == "OUTLINE_SEGMENT_ZERO_LENGTH" for i in report.errors)
    assert not any(i.code == "OUTLINE_NOT_CLOSED" for i in report.issues)


def test_valid_closed_outline_keeps_existing_closure_semantics():
    board = BoardModel(
        outline=[
            _segment("E1", (0.0, 0.0), (10.0, 0.0)),
            _segment("E2", (10.0, 0.0), (10.0, 5.0)),
            _segment("E3", (10.0, 5.0), (0.0, 5.0)),
            _segment("E4", (0.0, 5.0), (0.0, 0.0)),
        ]
    )

    report = validate_board(board, outline_tolerance_mm=0.01)

    assert report.ok
    assert not any(i.code.startswith("OUTLINE_") for i in report.issues)
