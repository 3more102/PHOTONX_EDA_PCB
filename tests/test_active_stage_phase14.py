from photonx_eda_pcb.active_stages import detect_opamp_comparator_stages
class I:
    def __init__(self,kind):self.kind=kind
def test_opamp_pin_role_candidate():
    ids={"U1":I("opamp")}
    pins={"U1":{"1":"VINP","2":"VINN","3":"VOUT"}}
    names={"U1":{"1":"IN+","2":"IN-","3":"OUT"}}
    x=detect_opamp_comparator_stages(ids,pins,names)[0]
    assert x.kind=="opamp_stage" and x.confidence==.9
