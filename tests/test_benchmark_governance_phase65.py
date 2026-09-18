from photonx_eda_pcb.benchmark_governance import BenchmarkPolicy,evaluate_benchmark
def test_benchmark_policy_blocks_regression():
    p=BenchmarkPolicy("connectivity",1.2,.5,1000)
    r=evaluate_benchmark(p,before=1.0,after=1.3,reduction_ratio=.8,peak_memory_bytes=500)
    assert not r.passed and "BENCHMARK_RUNTIME_REGRESSION" in r.blockers
