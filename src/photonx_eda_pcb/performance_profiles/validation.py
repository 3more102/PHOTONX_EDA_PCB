def validate_benchmark(r):
    issues=[]
    if not r.samples:issues.append("BENCHMARK_NO_SAMPLES")
    if min((s.seconds for s in r.samples),default=0)<0:issues.append("BENCHMARK_NEGATIVE_TIME")
    if r.min_seconds>r.max_seconds:issues.append("BENCHMARK_MIN_MAX")
    return issues
