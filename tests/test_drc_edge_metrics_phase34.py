from photonx_eda_pcb.models import BoardModel,PadCandidate,Point,OutlineSegment,CopperRegion
from photonx_eda_pcb.drc.edge_metrics import edge_clearance_metrics
def test_edge_metrics_closed_outline():
    pts=[Point(0,0),Point(5,0),Point(5,5),Point(0,5)]
    o=[OutlineSegment(str(i),pts[i],pts[(i+1)%4]) for i in range(4)]
    b=BoardModel(pads=[PadCandidate("P",Point(2.5,2.5),1,1,"C","F.Cu")],outline=o)
    m=edge_clearance_metrics(b)
    assert m["closed_outline"] and m["outside_objects"]==0 and m["minimum_clearance_mm"]==2.0


def test_edge_metrics_include_copper_regions():
    pts=[Point(0,0),Point(5,0),Point(5,5),Point(0,5)]
    o=[OutlineSegment(str(i),pts[i],pts[(i+1)%4]) for i in range(4)]
    region=CopperRegion(
        "R1",
        (Point(.25,1),Point(1.25,1),Point(1.25,2),Point(.25,2),Point(.25,1)),
        "F.Cu",
    )
    b=BoardModel(
        pads=[PadCandidate("P",Point(2.5,2.5),1,1,"C","F.Cu")],
        regions=[region],
        outline=o,
    )
    m=edge_clearance_metrics(b)
    assert m["objects"]==2
    assert m["outside_objects"]==0
    assert m["minimum_clearance_mm"]==0.25
