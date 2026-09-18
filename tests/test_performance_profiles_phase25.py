from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.performance_profiles.validation import validate_benchmark
def test_benchmark_collects_samples():
    r=benchmark("list",lambda:list(range(10)),iterations=2,warmup=0)
    assert len(r.samples)==2 and r.median_seconds>=0
    assert validate_benchmark(r)==[]
