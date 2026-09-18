from photonx_eda_pcb.models import BoardModel,PadCandidate,DrillHit,Point
from photonx_eda_pcb.drc.drill_copper import check_drill_copper_clearance
from photonx_eda_pcb.drc.model import DrcConfig
def test_unknown_plating_does_not_overclaim_error():
    b=BoardModel(pads=[PadCandidate("P",Point(.7,0),.4,.4,"C","F.Cu")],drills=[DrillHit("D",Point(0,0),1.0,"unknown")])
    issues=check_drill_copper_clearance(b,DrcConfig(min_drill_copper_clearance_mm=.2))
    assert issues and all(x.severity=="warning" for x in issues)
