from photonx_eda_pcb.protocol_detection.model import ProtocolCandidate
from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.peripheral_mapping import infer_peripheral_map
from photonx_eda_pcb.constraint_synthesis import synthesize_constraints
from photonx_eda_pcb.netclass_generation import generate_netclasses
class I:
    def __init__(self,kind): self.kind=kind; self.value=""; self.mpn=""
def test_semantics_to_constraints_flow():
    n=Netlist({"tx":[NetConnection("U1","1"),NetConnection("J1","1")],"rx":[NetConnection("U1","2"),NetConnection("J1","2")]},{"tx":"UART_TX","rx":"UART_RX"})
    g=build_schematic_graph(n)
    pmap=infer_peripheral_map([ProtocolCandidate("UART",("tx","rx"),.85,("labels",))],g,{"U1":I("mcu"),"J1":I("connector")})
    assert any(x.role=="controller" for x in pmap.bindings)
    roles={"tx":("protocol:UART",),"rx":("protocol:UART",)}
    cs=synthesize_constraints(["tx","rx"],roles)
    classes=generate_netclasses(cs,roles)
    assert sum(len(c.nets) for c in classes)==2
