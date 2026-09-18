from photonx_eda_pcb.repeated_circuits.model import CircuitInstance,RepeatedCircuitGroup
from photonx_eda_pcb.channel_detection import detect_channels,validate_channel
class I:
    def __init__(self,kind):self.kind=kind
def test_led_channel_classification():
    inst=(CircuitInstance("a","R1",("R1","D1"),("N1",),"h",1,()),CircuitInstance("b","R2",("R2","D2"),("N2",),"h",1,()))
    g=RepeatedCircuitGroup("g",inst,"t",1,.95,())
    ids={"R1":I("resistor"),"D1":I("led"),"R2":I("resistor"),"D2":I("led")}
    c=detect_channels([g],ids,{})[0]
    assert c.kind=="led_driver" and validate_channel(c)==[]
