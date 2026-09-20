from pathlib import Path
from photonx_eda_pcb import reconstruct
from photonx_eda_pcb.validation import validate_board
from photonx_eda_pcb.models import BoardModel, NetGroup
FIX=Path(__file__).parent/"fixtures"/"led"

def test_validation_catches_fake_net_member():
    board=reconstruct(FIX).board; board.nets[0].members.append("does_not_exist"); report=validate_board(board); assert not report.ok; assert any(i.code=="NET_MEMBER_MISSING" for i in report.errors)

def test_outline_is_closed_for_fixture():
    report=reconstruct(FIX).validation; assert not any(i.code=="OUTLINE_NOT_CLOSED" for i in report.issues)


def test_validation_rejects_duplicate_physical_net_ids():
    board=BoardModel(
        nets=[
            NetGroup("N1",[],1.0,"A"),
            NetGroup("N1",[],1.0,"B"),
        ]
    )
    report=validate_board(board)
    assert not report.ok
    assert any(
        issue.code=="DUPLICATE_NET_ID"
        and issue.object_ids==("N1",)
        for issue in report.errors
    )
