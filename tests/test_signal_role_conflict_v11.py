from photonx_eda_pcb.signal_role_synthesis.model import SignalRole
from photonx_eda_pcb.signal_role_synthesis.conflicts import role_conflicts
def test_role_conflict():
    assert role_conflicts(SignalRole("n",("power","ground"),.8))==["POWER_GROUND_CONFLICT"]
