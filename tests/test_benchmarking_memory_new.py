from photonx_eda_pcb.benchmarking.memory import measure_peak_bytes

def test_peak_memory_measurement_returns_result():
    value,peak=measure_peak_bytes(lambda:[0]*100)
    assert len(value)==100 and peak>=0
