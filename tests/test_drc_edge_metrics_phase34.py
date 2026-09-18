from photonx_eda_pcb.models import BoardModel,PadCandidate,Point,OutlineSegment
from photonx_eda_pcb.drc.edge_metrics import edge_clearance_metrics
def test_edge_metrics_closed_outline():
    pts=[Point(0,0),Point(5,0),Point(5,5),Point(0,5)]
    o=[OutlineSegment(str(i),pts[i],pts[(i+1)%4]) for i in range(4)]
    b=BoardModel(pads=[PadCandidate("P",Point(2.5,2.5),1,1,"C","F.Cu")],outline=o)
    m=edge_clearance_metrics(b)
    assert m["closed_outline"] and m["outside_objects"]==0 and m["minimum_clearance_mm"]==2.0
