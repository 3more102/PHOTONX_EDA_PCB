from photonx_eda_pcb.connector_pinout import infer_pinout,validate_pinout
from photonx_eda_pcb.connector_pinout.power import power_pins,ground_pins
def test_pinout_roles():
    p=infer_pinout("J1",{"1":"v","2":"g","3":"s"},{"v":"+5V","g":"GND","s":"UART_TX"})
    assert [x.pin_id for x in power_pins(p)]==["1"]
    assert [x.pin_id for x in ground_pins(p)]==["2"]
    assert validate_pinout(p)==[]
