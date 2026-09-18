from photonx_eda_pcb.filter_inference import detect_lc_filters,lc_resonance_hz
class I:
    def __init__(self,kind,value=None):self.kind=kind;self.value=value
def test_lc_filter_candidate():
    ids={"L1":I("inductor","10uH"),"C1":I("capacitor","1uF")}
    pins={"L1":{"1":"VIN","2":"VOUT"},"C1":{"1":"VOUT","2":"GND"}}
    f=detect_lc_filters(ids,pins,["GND"])[0]
    assert f.kind=="lc_filter" and f.confidence==.8
    assert lc_resonance_hz(10e-6,1e-6)>0
