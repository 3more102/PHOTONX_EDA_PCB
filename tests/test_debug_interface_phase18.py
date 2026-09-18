from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.debug_interface_inference import infer_debug_interfaces,validate_debug_interface
def test_swd_detection():
    n=Netlist({"io":[NetConnection("U1","1"),NetConnection("J1","1")],"clk":[NetConnection("U1","2"),NetConnection("J1","2")]},{"io":"SWDIO","clk":"SWCLK"})
    g=build_schematic_graph(n)
    x=infer_debug_interfaces(n.labels,g)[0]
    assert x.protocol=="SWD" and set(x.nets)=={"io","clk"} and x.confidence>.8
    assert validate_debug_interface(x)==[]
