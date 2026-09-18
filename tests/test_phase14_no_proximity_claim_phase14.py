from photonx_eda_pcb.bias_networks import detect_voltage_dividers
class I:
    def __init__(self,kind):self.kind=kind
def test_disconnected_resistors_are_not_divider():
    ids={"R1":I("resistor"),"R2":I("resistor")}
    pins={"R1":{"1":"A","2":"B"},"R2":{"1":"C","2":"D"}}
    assert detect_voltage_dividers(ids,pins,[],[])==[]
