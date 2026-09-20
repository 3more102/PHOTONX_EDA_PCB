from photonx_eda_pcb.drc.clearance import (
    check_unresolved_clearance,
    check_unresolved_clearance_bruteforce,
)
from photonx_eda_pcb.drc.model import DrcConfig
from photonx_eda_pcb.models import BoardModel, Point, Track
from photonx_eda_pcb.review_queue import build_board_review_queue


def _board(a_net=None, b_net="N2"):
    return BoardModel(
        tracks=[
            Track("a", Point(0, 0), Point(2, 0), 0.2, "F.Cu", a_net),
            Track("b", Point(0, 0.2), Point(2, 0.2), 0.2, "F.Cu", b_net),
        ]
    )


def test_unresolved_close_copper_is_warning_not_error():
    issues = check_unresolved_clearance(_board(), DrcConfig())

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].code == "COPPER_CLEARANCE_UNRESOLVED"
    assert issues[0].object_ids == ("a", "b")


def test_known_net_relationships_are_not_unresolved_reviews():
    cfg = DrcConfig()

    assert check_unresolved_clearance(_board("N1", "N2"), cfg) == []
    assert check_unresolved_clearance(_board("N1", "N1"), cfg) == []


def test_unresolved_clearance_spatial_and_bruteforce_paths_match():
    board = _board()
    cfg = DrcConfig()

    assert check_unresolved_clearance(board, cfg) == check_unresolved_clearance_bruteforce(
        board, cfg
    )


def test_review_queue_surfaces_unresolved_clearance_by_default():
    queue = build_board_review_queue(_board())
    item = next(item for item in queue.all() if item.kind == "clearance")

    assert item.target_id == "a"
    assert item.metadata["code"] == "COPPER_CLEARANCE_UNRESOLVED"
    assert item.metadata["object_ids"] == ("a", "b")
    assert item.metadata["selectable_object_id"] == "a"
    assert item.metadata["confidence_available"] is False


def test_review_queue_can_disable_unresolved_clearance_review():
    queue = build_board_review_queue(
        _board(),
        include_unresolved_clearance=False,
    )

    assert all(item.kind != "clearance" for item in queue.all())
