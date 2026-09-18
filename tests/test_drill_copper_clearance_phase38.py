from photonx_eda_pcb.models import BoardModel,PadCandidate,DrillHit,Point
from photonx_eda_pcb.drc.drill_copper import check_drill_copper_clearance
from photonx_eda_pcb.drc.model import DrcConfig
def test_non_plated_drill_near_unrelated_copper_is_error():
    b=BoardModel(pads=[PadCandidate("P",Point(1,0),1,1,"C","F.Cu",net_id="N")],drills=[DrillHit("D",Point(0,0),1.0,"non-plated")])
    issues=check_drill_copper_clearance(b,DrcConfig(min_drill_copper_clearance_mm=.6))
    assert any(x.code=="DRILL_COPPER_CLEARANCE" and x.severity=="error" for x in issues)
