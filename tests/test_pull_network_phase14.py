from photonx_eda_pcb.bias_networks import detect_pull_networks
class I:
    def __init__(self,kind):self.kind=kind
def test_pull_up_and_down():
    ids={"R1":I("resistor"),"R2":I("resistor")}
    pins={"R1":{"1":"VCC","2":"SIG1"},"R2":{"1":"GND","2":"SIG2"}}
    kinds={x.kind for x in detect_pull_networks(ids,pins,["VCC"],["GND"])}
    assert kinds=={"pull_up","pull_down"}
