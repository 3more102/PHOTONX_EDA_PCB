from photonx_eda_pcb.models import BoardModel, NetGroup, PadCandidate, Point
from photonx_eda_pcb.validation import validate_board


def _pad(net_id=None):
    return PadCandidate(
        id="P1",
        center=Point(0.0, 0.0),
        size_x=1.0,
        size_y=1.0,
        shape="C",
        layer="F.Cu",
        net_id=net_id,
    )


def _error_codes(board):
    return [issue.code for issue in validate_board(board).errors]


def test_net_backref_must_match_the_specific_physical_net():
    board = BoardModel(
        pads=[_pad("N1")],
        nets=[
            NetGroup("N1", [], 0.99),
            NetGroup("N2", ["P1"], 0.99),
        ],
    )

    codes = _error_codes(board)

    assert "OBJECT_NET_BACKREF_MISMATCH" in codes
    assert "OBJECT_IN_MULTIPLE_NETS" not in codes


def test_forward_net_membership_requires_matching_object_backref():
    board = BoardModel(
        pads=[_pad()],
        nets=[NetGroup("N1", ["P1"], 0.99)],
    )

    assert "OBJECT_NET_BACKREF_MISMATCH" in _error_codes(board)


def test_duplicate_member_inside_one_net_is_not_reported_as_multiple_nets():
    board = BoardModel(
        pads=[_pad("N1")],
        nets=[NetGroup("N1", ["P1", "P1"], 0.99)],
    )

    codes = _error_codes(board)

    assert "NET_MEMBER_DUPLICATE" in codes
    assert "OBJECT_IN_MULTIPLE_NETS" not in codes


def test_object_in_two_distinct_nets_remains_a_cross_net_error():
    board = BoardModel(
        pads=[_pad("N1")],
        nets=[
            NetGroup("N1", ["P1"], 0.99),
            NetGroup("N2", ["P1"], 0.99),
        ],
    )

    assert "OBJECT_IN_MULTIPLE_NETS" in _error_codes(board)


def test_duplicate_physical_net_ids_are_rejected():
    board = BoardModel(
        nets=[
            NetGroup("N1", [], 0.99),
            NetGroup("N1", [], 0.95),
        ],
    )

    assert "DUPLICATE_NET_ID" in _error_codes(board)
