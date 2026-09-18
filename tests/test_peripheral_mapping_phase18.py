from photonx_eda_pcb.protocol_detection.model import ProtocolCandidate
from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.peripheral_mapping import infer_peripheral_map,validate_peripheral_map
class I:
    def __init__(self,kind): self.kind=kind; self.value=""; self.mpn=""
def test_peripheral_map_controller_and_peer():
    n=Netlist({"scl":[NetConnection("U1","1"),NetConnection("U2","1")],"sda":[NetConnection("U1","2"),NetConnection("U2","2")]},{})
    g=build_schematic_graph(n)
    p=[ProtocolCandidate("I2C",("scl","sda"),.8,("labels",))]
    m=infer_peripheral_map(p,g,{"U1":I("mcu"),"U2":I("sensor")})
    by={x.component_id:x for x in m.bindings}
    assert by["U1"].role=="controller" and by["U2"].role=="peripheral"
    assert by["U1"].peer_components==("U2",)
    assert validate_peripheral_map(m)==[]
