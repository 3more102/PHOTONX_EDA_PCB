from photonx_eda_pcb.wire_routing.model import WireRoute
from photonx_eda_pcb.wire_routing.crossings import count_crossings
def test_crossing_count():
    a=WireRoute("A",((0,5),(10,5)))
    b=WireRoute("B",((5,0),(5,10)))
    assert count_crossings([a,b])==1
