from photonx_eda_pcb.memory_metrics import measure_peak_memory,memory_delta
def test_memory_measurement():
    a=measure_peak_memory("a",lambda:[0]*100)
    b=measure_peak_memory("b",lambda:[0]*200)
    assert a.peak_bytes>=0 and b.peak_bytes>=0
    assert "peak_delta_bytes" in memory_delta(a,b)
