from photonx_eda_pcb.models import BoardModel,PadCandidate,DrillHit,Point
from photonx_eda_pcb.drc.drill_copper import check_drill_copper_clearance
from photonx_eda_pcb.drc.model import DrcConfig
def test_associated_drilled_pad_is_not_self_violation():
    p=PadCandidate("P",Point(0,0),2,2,"C","F.Cu",drill=.8)
    d=DrillHit("D",Point(0,0),.8,"plated")
    assert check_drill_copper_clearance(BoardModel(pads=[p],drills=[d]),DrcConfig())==[]
