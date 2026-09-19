from photonx_eda_pcb.models import BoardModel, OutlineSegment, Point
from photonx_eda_pcb.validation import validate_board


def _segment(segment_id, start, end):
    return OutlineSegment(segment_id, Point(*start), Point(*end))


def _rectangle(prefix, x0, y0, x1, y1):
    return [
        _segment(f"{prefix}1", (x0, y0), (x1, y0)),
        _segment(f"{prefix}2", (x1, y0), (x1, y1)),
        _segment(f"{prefix}3", (x1, y1), (x0, y1)),
        _segment(f"{prefix}4", (x0, y1), (x0, y0)),
    ]


def test_bow_tie_outline_is_rejected_even_when_every_endpoint_has_degree_two():
    board = BoardModel(
        outline=[
            _segment("E1", (0.0, 0.0), (2.0, 2.0)),
            _segment("E2", (2.0, 2.0), (0.0, 2.0)),
            _segment("E3", (0.0, 2.0), (2.0, 0.0)),
            _segment("E4", (2.0, 0.0), (0.0, 0.0)),
        ]
    )

    report = validate_board(board, outline_tolerance_mm=0.01)

    assert not report.ok
    issue = next(i for i in report.errors if i.code == "OUTLINE_SELF_INTERSECTION")
    assert issue.object_ids == ("E1", "E3")
    assert not any(i.code == "OUTLINE_NOT_CLOSED" for i in report.issues)


def test_duplicate_reversed_outline_edge_is_rejected_as_overlap():
    board = BoardModel(
        outline=[
            _segment("E1", (0.0, 0.0), (2.0, 0.0)),
            _segment("E2", (2.0, 0.0), (0.0, 0.0)),
        ]
    )

    report = validate_board(board, outline_tolerance_mm=0.01)

    assert not report.ok
    issue = next(i for i in report.errors if i.code == "OUTLINE_SELF_INTERSECTION")
    assert issue.object_ids == ("E1", "E2")


def test_disjoint_closed_outline_loops_remain_valid_for_cutout_style_geometry():
    board = BoardModel(
        outline=[
            *_rectangle("O", 0.0, 0.0, 10.0, 8.0),
            *_rectangle("I", 3.0, 2.0, 5.0, 4.0),
        ]
    )

    report = validate_board(board, outline_tolerance_mm=0.01)

    assert report.ok
    assert not any(i.code == "OUTLINE_SELF_INTERSECTION" for i in report.issues)
