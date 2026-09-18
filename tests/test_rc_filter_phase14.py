from photonx_eda_pcb.filter_inference import detect_rc_filters,rc_cutoff_hz
class I:
    def __init__(self,kind,value=None):self.kind=kind;self.value=value
def test_grounded_rc_filter_with_cutoff():
    ids={"R1":I("resistor","10kΩ"),"C1":I("capacitor","100nF")}
    pins={"R1":{"1":"IN","2":"OUT"},"C1":{"1":"OUT","2":"GND"}}
    f=detect_rc_filters(ids,pins,["GND"])[0]
    assert f.confidence>.8 and "estimated_cutoff_hz" in dict(f.parameters)
    assert 150<rc_cutoff_hz(10000,100e-9)<170
