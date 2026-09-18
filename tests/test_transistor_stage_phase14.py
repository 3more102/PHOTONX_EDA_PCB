from photonx_eda_pcb.transistor_stages import detect_transistor_stages
class I:
    def __init__(self,kind):self.kind=kind
def test_mosfet_stage_with_gate_resistor():
    ids={"Q1":I("mosfet"),"R1":I("resistor")}
    pins={"Q1":{"1":"CTRL","2":"GND","3":"LOAD"},"R1":{"1":"IN","2":"CTRL"}}
    names={"Q1":{"1":"G","2":"S","3":"D"}}
    x=detect_transistor_stages(ids,pins,names,[],["GND"])[0]
    assert x.kind=="transistor_stage" and "control_bias_resistor" in x.evidence
