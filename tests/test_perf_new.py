from photonx_eda_pcb.perf.counter import CounterSet
from photonx_eda_pcb.perf.sampling import deterministic_sample
def test_perf_helpers():
    counters=CounterSet(); counters.inc("pads",2); assert counters.snapshot()=={"pads":2}
    assert deterministic_sample(list(range(10)),3)==[0,3,6]
