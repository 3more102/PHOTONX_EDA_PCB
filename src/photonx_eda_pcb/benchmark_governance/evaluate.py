from .model import BenchmarkDecision
def evaluate_benchmark(policy,*,before=None,after=None,reduction_ratio=None,peak_memory_bytes=None):
    blockers=[];evidence={}
    if before is not None and after is not None and before>0:
        ratio=float(after)/float(before);evidence["runtime_ratio"]=ratio
        if ratio>policy.max_regression_ratio:blockers.append("BENCHMARK_RUNTIME_REGRESSION")
    if reduction_ratio is not None:
        evidence["pair_reduction"]=float(reduction_ratio)
        if float(reduction_ratio)<policy.min_pair_reduction:blockers.append("BENCHMARK_PAIR_REDUCTION_LOW")
    if policy.max_peak_memory_bytes is not None and peak_memory_bytes is not None:
        evidence["peak_memory_bytes"]=int(peak_memory_bytes)
        if int(peak_memory_bytes)>policy.max_peak_memory_bytes:blockers.append("BENCHMARK_MEMORY_BUDGET")
    return BenchmarkDecision(policy.name,not blockers,tuple(blockers),evidence)
