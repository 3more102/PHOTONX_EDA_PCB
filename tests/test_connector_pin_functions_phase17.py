from photonx_eda_pcb.protocol_detection.model import ProtocolCandidate
from photonx_eda_pcb.connector_pin_functions import infer_connector_pin_functions,resolve_pin_functions,validate_pin_function
def test_i2c_power_connector_functions():
    pinmap={"1":"GND","2":"VBUS","3":"SDA","4":"SCL"}
    labels={"GND":"GND","VBUS":"VBUS","SDA":"SDA","SCL":"SCL"}
    proto=[ProtocolCandidate("I2C",("SDA","SCL"),.8,("labels",))]
    r=resolve_pin_functions(infer_connector_pin_functions("J1",pinmap,net_labels=labels,protocols=proto,power_nets=["VBUS"],ground_nets=["GND"]))
    by={x.pin:x for x in r}
    assert by["1"].function=="ground" and by["2"].function=="power"
    assert by["3"].function=="i2c_sda" and by["4"].function=="i2c_scl"
    assert all(validate_pin_function(x)==[] for x in r)
