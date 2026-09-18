from photonx_eda_pcb.stress_harness import StressCase,run_stress_case,ResourceLimits
from photonx_eda_pcb.stress_harness.assertions import assert_within_limits
def test_stress_runner():
    r=run_stress_case(StressCase("sum",100,2),sum,[1,2,3])
    assert r["result"]==6 and len(r["samples"])==2
    assert assert_within_limits(r,ResourceLimits(5,1000),3)==[]
