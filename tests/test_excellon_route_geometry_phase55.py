from photonx_eda_pcb.excellon_routing import RoutedPath,route_shape
from photonx_eda_pcb.excellon_routing.measure import route_length_mm,route_segment_count
def test_route_geometry_and_measure():
    r=RoutedPath("r",((0,0),(3,0),(3,4)),1.0)
    s=route_shape(r)
    assert route_length_mm(r)==7.0 and route_segment_count(r)==2
    assert s.bounds==(-.5,-.5,3.5,4.5)
