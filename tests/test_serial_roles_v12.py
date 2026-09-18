from photonx_eda_pcb.serial_endpoints.model import Endpoint,SerialLink
from photonx_eda_pcb.serial_endpoints.roles import component_roles
def test_component_roles():
    l=SerialLink("SPI",("a","b"),(Endpoint("U1","1","MOSI"),Endpoint("U1","2","SCLK"),Endpoint("U2","3","MOSI")),.8)
    assert component_roles(l)["U1"]==("MOSI","SCLK")
