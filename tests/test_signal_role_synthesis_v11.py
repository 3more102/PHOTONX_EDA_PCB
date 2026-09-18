from photonx_eda_pcb.clock_inference.model import ClockCandidate
from photonx_eda_pcb.reset_inference.model import ResetCandidate
from photonx_eda_pcb.bus_grouping.model import BusCandidate
from photonx_eda_pcb.signal_role_synthesis import synthesize_roles
def test_signal_role_synthesis():
    roles=synthesize_roles(["n0","n1"],clock=[ClockCandidate("n0",.9)],reset=[ResetCandidate("n1",True,.8)],buses=[BusCandidate("DATA",("n0","n1"),(0,1),2,.8)])
    by={x.net_id:x.roles for x in roles}
    assert "clock" in by["n0"] and "bus:DATA" in by["n0"]
    assert "reset" in by["n1"]
