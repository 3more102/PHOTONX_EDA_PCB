from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.topology_analytics import build_net_component_graph,topology_metrics
def test_topology_metrics():
    n=Netlist({"N1":[NetConnection("R1","1"),NetConnection("U1","1")]},{})
    g=build_net_component_graph(build_schematic_graph(n))
    m=topology_metrics(g)
    assert m["nodes"]==3 and m["edges"]==2 and m["components"]==1
