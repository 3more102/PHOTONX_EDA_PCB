from .clock import now_ns,elapsed_seconds
from .result import BenchmarkResult
def run_case(case):
    case.validate()
    try:
        for _ in range(case.warmup):case.fn()
        durations=[]
        for _ in range(case.iterations):
            s=now_ns();case.fn();durations.append(elapsed_seconds(s,now_ns()))
        return BenchmarkResult(case.name,durations,dict(case.metadata))
    except Exception as e:return BenchmarkResult(case.name,[],dict(case.metadata),f'{type(e).__name__}: {e}')
def run_suite(cases):return [run_case(c) for c in cases]
