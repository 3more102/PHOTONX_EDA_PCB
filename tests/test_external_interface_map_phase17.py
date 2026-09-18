from photonx_eda_pcb.connector_pin_functions.model import ResolvedPinFunction
from photonx_eda_pcb.port_inference.model import PortCandidate
from photonx_eda_pcb.external_interface_map import build_external_interface_map,validate_interface_map
from photonx_eda_pcb.external_interface_map.coverage import interface_coverage
def test_interface_map():
    pins=[ResolvedPinFunction("J1","1","GND","ground",.99),ResolvedPinFunction("J1","2","SDA","i2c_sda",.9)]
    ports=[PortCandidate("J1","i2c",("2",),("SDA",),.8)]
    m=build_external_interface_map(pins,ports)
    assert m.confidence>0 and not m.unresolved and interface_coverage(m)==1.0
    assert validate_interface_map(m)==[]
