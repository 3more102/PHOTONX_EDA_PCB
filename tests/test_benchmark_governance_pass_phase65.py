from photonx_eda_pcb.benchmark_governance import BenchmarkPolicy,evaluate_benchmark
def test_benchmark_policy_pass():
    r=evaluate_benchmark(BenchmarkPolicy("x",1.3,.5,1000),before=1,after=.8,reduction_ratio=.9,peak_memory_bytes=500)
    assert r.passed
