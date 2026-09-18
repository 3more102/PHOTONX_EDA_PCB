from photonx_eda_pcb.stress_corpus import grid_board
from photonx_eda_pcb.stress_corpus.workloads import connectivity_workload
from photonx_eda_pcb.performance_profiles import benchmark
def test_connectivity_benchmark_smoke():
    b=grid_board(12,12,pitch_mm=2.0)
    r=benchmark("connectivity",connectivity_workload(b),iterations=1,warmup=0)
    assert r.median_seconds>=0 and r.samples[0].result_size is not None
