from photonx_eda_pcb.models import BoardModel,PadCandidate,Point,OutlineSegment
from photonx_eda_pcb.drc.edge import check_edge_presence
from photonx_eda_pcb.drc.model import DrcConfig
def outline():
    p=[Point(0,0),Point(10,0),Point(10,10),Point(0,10)]
    return [OutlineSegment(str(i),p[i],p[(i+1)%4]) for i in range(4)]
def test_exact_edge_clearance_and_outside_detection():
    b=BoardModel(pads=[
      PadCandidate("safe",Point(5,5),1,1,"C","F.Cu"),
      PadCandidate("near",Point(.55,5),1,1,"C","F.Cu"),
      PadCandidate("outside",Point(10.2,5),1,1,"C","F.Cu"),
    ],outline=outline())
    issues=check_edge_presence(b,DrcConfig(edge_clearance_mm=.1))
    by={x.object_ids[0]:x.code for x in issues}
    assert "safe" not in by
    assert by["near"]=="COPPER_EDGE_CLEARANCE"
    assert by["outside"]=="COPPER_OUTSIDE_BOARD"
