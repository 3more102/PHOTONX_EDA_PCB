import time,statistics
from .model import BenchmarkSample,BenchmarkResult
def benchmark(name,fn,iterations=3,warmup=1):
    for _ in range(max(0,int(warmup))):fn()
    samples=[]
    for _ in range(max(1,int(iterations))):
        t=time.perf_counter();value=fn();dt=time.perf_counter()-t
        size=len(value) if hasattr(value,"__len__") else None
        samples.append(BenchmarkSample(dt,size))
    vals=[x.seconds for x in samples]
    return BenchmarkResult(str(name),tuple(samples),statistics.median(vals),min(vals),max(vals))
