from photonx_eda_pcb.drc.drill_copper import check_drill_copper_clearance
from photonx_eda_pcb.drc.edge import check_edge_presence
from photonx_eda_pcb.drc.mechanical_clearance import check_mechanical_features
from photonx_eda_pcb.drc.model import DrcConfig
from photonx_eda_pcb.excellon_routing.drc import check_route_copper_clearance
from photonx_eda_pcb.excellon_routing.model import RoutedPath
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import BoardModel,CopperRegion,DrillHit,OutlineSegment,Point


def _region(region_id="R",x0=1.0,y0=1.0,x1=3.0,y1=3.0,*,holes=()):
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
        holes=holes,
    )


def _outline():
    pts=(Point(0,0),Point(10,0),Point(10,10),Point(0,10))
    return [OutlineSegment(str(i),pts[i],pts[(i+1)%4]) for i in range(4)]


def test_drill_clearance_checks_copper_regions():
    board=BoardModel(
        drills=[DrillHit("D",Point(2,2),.4,"non-plated")],
        regions=[_region()],
    )
    issues=check_drill_copper_clearance(
        board,DrcConfig(min_drill_copper_clearance_mm=.15)
    )
    assert any(
        issue.code=="DRILL_COPPER_CLEARANCE"
        and issue.object_ids==("D","R")
        and issue.severity=="error"
        for issue in issues
    )


def test_mechanical_clearance_checks_copper_regions():
    board=BoardModel(regions=[_region()])
    slot=SlotFeature("S",(1.5,2.0),(2.5,2.0),.2,"non-plated")
    issues=check_mechanical_features([slot],board,.15)
    assert any(
        issue.code=="MECHANICAL_COPPER_CLEARANCE"
        and issue.object_ids==("S","R")
        and issue.severity=="error"
        for issue in issues
    )


def test_routed_feature_clearance_checks_copper_regions():
    board=BoardModel(regions=[_region()])
    route=RoutedPath("RP",((1.5,2.0),(2.5,2.0)),.2,"non-plated")
    issues=check_route_copper_clearance([route],board,.15)
    assert any(
        issue.code=="ROUTE_COPPER_CLEARANCE"
        and issue.object_ids==("RP","R")
        and issue.severity=="error"
        for issue in issues
    )


def test_board_edge_clearance_checks_copper_regions():
    board=BoardModel(
        regions=[_region(x0=.05,y0=1.0,x1=.5,y1=2.0)],
        outline=_outline(),
    )
    issues=check_edge_presence(board,DrcConfig(edge_clearance_mm=.1))
    assert any(
        issue.code=="COPPER_EDGE_CLEARANCE"
        and issue.object_ids==("R",)
        for issue in issues
    )


def test_region_holes_remain_non_copper_for_drill_clearance():
    hole=(
        Point(1.5,1.5),
        Point(1.5,2.5),
        Point(2.5,2.5),
        Point(2.5,1.5),
        Point(1.5,1.5),
    )
    board=BoardModel(
        drills=[DrillHit("D",Point(2,2),.2,"non-plated")],
        regions=[_region(holes=(hole,))],
    )
    issues=check_drill_copper_clearance(
        board,DrcConfig(min_drill_copper_clearance_mm=.15)
    )
    assert not any(issue.object_ids==("D","R") for issue in issues)
