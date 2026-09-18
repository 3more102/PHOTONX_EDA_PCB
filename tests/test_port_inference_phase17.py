from photonx_eda_pcb.connector_pin_functions.model import ResolvedPinFunction
from photonx_eda_pcb.port_inference import infer_ports,validate_port
def test_uart_and_power_ports():
    pins=[ResolvedPinFunction("J1","1","TX","uart_tx",.9),ResolvedPinFunction("J1","2","RX","uart_rx",.9),ResolvedPinFunction("J1","3","GND","ground",.99)]
    ports=infer_ports(pins)
    kinds={x.kind for x in ports}
    assert {"uart","power"}<=kinds
    assert all(validate_port(x)==[] for x in ports)
