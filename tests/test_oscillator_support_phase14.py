from photonx_eda_pcb.oscillator_support import detect_oscillator_support
class I:
    def __init__(self,kind):self.kind=kind
def test_crystal_with_load_caps():
    ids={"Y1":I("crystal"),"C1":I("capacitor"),"C2":I("capacitor")}
    pins={"Y1":{"1":"X1","2":"X2"},"C1":{"1":"X1","2":"GND"},"C2":{"1":"X2","2":"GND"}}
    x=detect_oscillator_support(ids,pins,["GND"])[0]
    assert dict(x.parameters)["grounded_capacitors"]==2 and x.confidence>.8
