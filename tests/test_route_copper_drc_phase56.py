from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.excellon_routing.drc import check_route_copper_clearance
from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
def test_unknown_route_near_copper_is_warning():
    route=RoutedPath("r",((0,0),(2,0)),.5,"unknown")
    b=BoardModel(pads=[PadCandidate("p",Point(1,.3),.2,.2,"C","F.Cu")])
    issues=check_route_copper_clearance([route],b,.1)
    assert issues and issues[0].severity=="warning"
