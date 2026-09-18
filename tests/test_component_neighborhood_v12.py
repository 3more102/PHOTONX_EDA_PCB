from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.component_neighborhood import build_neighborhood,validate_neighborhood
def test_component_neighborhood():
    n=Netlist({"N1":[NetConnection("R1","1"),NetConnection("U1","1")],"N2":[NetConnection("R1","2"),NetConnection("C1","1")]},{})
    g=build_schematic_graph(n)
    x=build_neighborhood("R1",g)
    assert x.degree==2 and x.neighbors==("C1","U1")
    assert validate_neighborhood(x)==[]
