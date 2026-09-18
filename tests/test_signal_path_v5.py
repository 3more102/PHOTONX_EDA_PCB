from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.signal_path import build_signal_graph,trace_path,validate_signal_path
def test_signal_path():
    n=Netlist({"N1":[NetConnection("J1","1"),NetConnection("R1","1")],"N2":[NetConnection("R1","2"),NetConnection("U1","1")]},{})
    g=build_signal_graph(build_schematic_graph(n))
    p=trace_path(g,"J1","U1")
    assert p is not None and p.hops==4 and validate_signal_path(p)==[]
