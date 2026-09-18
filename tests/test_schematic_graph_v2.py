from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph,validate_schematic_graph
def test_schematic_graph():
    n=Netlist({"N1":[NetConnection("R1","1"),NetConnection("LED1","A")]},{"N1":"LED_A"})
    g=build_schematic_graph(n,{"R1":"resistor","LED1":"led"})
    assert len(g.components)==2 and len(g.pin_edges)==2
    assert validate_schematic_graph(g)==[]
