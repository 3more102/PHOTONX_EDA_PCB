from photonx_eda_pcb.current_sense import detect_current_sense
class I:
    def __init__(self,kind,value=None):self.kind=kind;self.value=value
def test_low_ohm_shunt_candidate():
    ids={"RSH":I("resistor","0.05Ω")}
    pins={"RSH":{"1":"VIN","2":"LOAD"}}
    x=detect_current_sense(ids,pins)[0]
    assert x.kind=="current_sense" and dict(x.parameters)["resistance_ohm"]==.05
