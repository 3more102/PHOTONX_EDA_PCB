from photonx_eda_pcb.netclass_inference.model import NetClassCandidate
from photonx_eda_pcb.netclass_inference.constraints import constraints_for
def test_power_constraints():
    c=constraints_for(NetClassCandidate("p","power",.9))
    assert c["min_width_mm"]>=.3
