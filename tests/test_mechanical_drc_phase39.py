from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.drc.mechanical_clearance import check_mechanical_features
from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
def test_mechanical_feature_drc():
    b=BoardModel(pads=[PadCandidate("P",Point(2,1),.5,.5,"C","F.Cu")])
    issues=check_mechanical_features([SlotFeature("S",(0,0),(4,0),1)],b,.3)
    assert any(x.code=="MECHANICAL_COPPER_CLEARANCE" for x in issues)
