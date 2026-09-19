from photonx_eda_pcb.drc.edge_metrics import edge_clearance_metrics
from photonx_eda_pcb.models import BoardModel,CopperRegion,OutlineSegment,PadCandidate,Point


def _outline():
    pts=(Point(0,0),Point(5,0),Point(5,5),Point(0,5))
    return [OutlineSegment(str(i),pts[i],pts[(i+1)%4]) for i in range(4)]


def _region(region_id,x0,y0,x1,y1):
    return CopperRegion(
        region_id,
        (
            Point(x0,y0),
            Point(x1,y0),
            Point(x1,y1),
            Point(x0,y1),
            Point(x0,y0),
        ),
        "F.Cu",
    )


def test_edge_metrics_include_copper_regions_in_count_and_minimum():
    board=BoardModel(
        pads=[PadCandidate("P",Point(2.5,2.5),1,1,"C","F.Cu")],
        regions=[_region("R",.1,1.0,.8,2.0)],
        outline=_outline(),
    )

    metrics=edge_clearance_metrics(board)

    assert metrics["closed_outline"] is True
    assert metrics["objects"]==2
    assert metrics["outside_objects"]==0
    assert metrics["minimum_clearance_mm"]==.1


def test_edge_metrics_count_outside_copper_regions():
    board=BoardModel(
        regions=[_region("R",-0.1,1.0,.8,2.0)],
        outline=_outline(),
    )

    metrics=edge_clearance_metrics(board)

    assert metrics["objects"]==1
    assert metrics["outside_objects"]==1
    assert metrics["minimum_clearance_mm"]==0.0
