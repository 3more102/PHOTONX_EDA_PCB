from photonx_eda_pcb.protocol_detection.model import ProtocolCandidate
from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.peripheral_mapping import infer_peripheral_map
from photonx_eda_pcb.mcu_interfaces import build_mcu_interfaces,validate_mcu_interface
class I:
    kind="microcontroller"; value=""; mpn=""
def test_mcu_interface_pins():
    n=Netlist({"tx":[NetConnection("U1","PA9"),NetConnection("J1","1")],"rx":[NetConnection("U1","PA10"),NetConnection("J1","2")]},{})
    g=build_schematic_graph(n)
    p=[ProtocolCandidate("UART",("tx","rx"),.9,("labels",))]
    m=infer_peripheral_map(p,g,{"U1":I()})
    interfaces=build_mcu_interfaces(m,g)
    u=[x for x in interfaces if x.component_id=="U1"][0]
    assert u.protocol=="UART" and ("PA9","tx") in u.pins
    assert validate_mcu_interface(u)==[]
