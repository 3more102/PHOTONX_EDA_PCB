from photonx_eda_pcb.benchmarking.case import BenchmarkCase
from photonx_eda_pcb.benchmarking.runner import run_case
from photonx_eda_pcb.benchmarking.statistics import duration_stats

def test_benchmark_runner_records_iterations():
    r=run_case(BenchmarkCase('noop',lambda:None,iterations=3,warmup=1))
    assert r.ok and r.count==3
    assert duration_stats(r.durations)['count']==3
