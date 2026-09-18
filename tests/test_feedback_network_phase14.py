from photonx_eda_pcb.feedback_networks import detect_feedback_networks
class I:
    def __init__(self,kind):self.kind=kind
def test_feedback_from_named_pin():
    ids={"U1":I("opamp"),"R1":I("resistor"),"R2":I("resistor")}
    pins={"U1":{"1":"FB","2":"OUT"},"R1":{"1":"FB","2":"OUT"},"R2":{"1":"FB","2":"GND"}}
    names={"U1":{"1":"IN-","2":"OUT"}}
    x=detect_feedback_networks(ids,pins,names)[0]
    assert x.kind=="feedback_network" and x.confidence>=.88
