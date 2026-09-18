from photonx_eda_pcb.board_diff.model import BoardDiff,DiffEntry
from photonx_eda_pcb.eco_tracking import eco_from_board_diff,validate_eco
from photonx_eda_pcb.eco_tracking.approval import approve_change,all_approved
def test_eco_from_diff():
    e=eco_from_board_diff(BoardDiff([DiffEntry("added","track:1"),DiffEntry("removed","pad:1")]))
    assert [x.action for x in e.changes]==["add","remove"]
    assert validate_eco(e)==[]
    e.changes=[approve_change(x) for x in e.changes]
    assert all_approved(e)
