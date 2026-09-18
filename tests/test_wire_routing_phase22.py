from photonx_eda_pcb.wire_routing import route_manhattan,validate_route
from photonx_eda_pcb.wire_routing.segments import route_length
def test_manhattan_route():
    r=route_manhattan("N1",(0,0),(10,5))
    assert r.points==((0.0,0.0),(10.0,0.0),(10.0,5.0))
    assert route_length(r)==15 and validate_route(r)==[]
