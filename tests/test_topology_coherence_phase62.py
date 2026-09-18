from photonx_eda_pcb.supply_domains.model import SupplyDomain
from photonx_eda_pcb.connector_pin_functions.model import ResolvedPinFunction
from photonx_eda_pcb.protocol_detection.model import ProtocolCandidate
from photonx_eda_pcb.topology_coherence import analyze_topology_coherence
def test_interface_pin_without_protocol_is_warning():
    d=[SupplyDomain("3V3",("VCC",),("GND",),("U1",),3.3,.9)]
    pins=[ResolvedPinFunction("J1","1","TX","UART_TX",.8)]
    r=analyze_topology_coherence(d,pins,[])
    assert any(x.code=="INTERFACE_PIN_WITHOUT_PROTOCOL" for x in r.findings)
