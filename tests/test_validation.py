from pathlib import Path
from photonx_eda_pcb import reconstruct
from photonx_eda_pcb.validation import validate_board
FIX=Path(__file__).parent/"fixtures"/"led"

def test_validation_catches_fake_net_member():
    board=reconstruct(FIX).board; board.nets[0].members.append("does_not_exist"); report=validate_board(board); assert not report.ok; assert any(i.code=="NET_MEMBER_MISSING" for i in report.errors)

def test_outline_is_closed_for_fixture():
    report=reconstruct(FIX).validation; assert not any(i.code=="OUTLINE_NOT_CLOSED" for i in report.issues)
