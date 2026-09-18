from photonx_eda_pcb.bias_networks import detect_voltage_dividers
class I:
    def __init__(self,kind,value=None):self.kind=kind;self.value=value
def test_supply_anchored_divider():
    ids={"R1":I("resistor","10kΩ"),"R2":I("resistor","10kΩ")}
    pins={"R1":{"1":"VCC","2":"MID"},"R2":{"1":"MID","2":"GND"}}
    x=detect_voltage_dividers(ids,pins,["VCC"],["GND"])[0]
    assert x.kind=="voltage_divider" and x.confidence==.9 and dict(x.parameters)["midpoint"]=="MID"
