from photonx_eda_pcb.models import BoardModel,OutlineSegment,PadCandidate,Point
from photonx_eda_pcb.drc.edge import check_edge_presence
from photonx_eda_pcb.drc.model import DrcConfig
def loop(prefix,pts):return [OutlineSegment(prefix+str(i),Point(*pts[i]),Point(*pts[(i+1)%len(pts)])) for i in range(len(pts))]
def test_copper_inside_cutout_is_outside_material():
    b=BoardModel(pads=[PadCandidate("P",Point(5,5),1,1,"C","F.Cu")],outline=loop("o",[(0,0),(10,0),(10,10),(0,10)])+loop("i",[(4,4),(6,4),(6,6),(4,6)]))
    issues=check_edge_presence(b,DrcConfig())
    assert any(x.code=="COPPER_OUTSIDE_BOARD" for x in issues)
