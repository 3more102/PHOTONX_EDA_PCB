from photonx_eda_pcb.repeated_circuits.model import CircuitInstance,RepeatedCircuitGroup
from photonx_eda_pcb.channel_consistency import compare_repeated_group
def test_channel_delta_visible():
    a=CircuitInstance("a","x",("U1",),("N1",),"fp",1.0)
    b=CircuitInstance("b","y",("U2",),("N2",),"other",.8,("R value differs",))
    g=RepeatedCircuitGroup("g",(a,b),"fp",.8,.8)
    r=compare_repeated_group(g)
    assert not r.consistent and len(r.deltas)>=2
