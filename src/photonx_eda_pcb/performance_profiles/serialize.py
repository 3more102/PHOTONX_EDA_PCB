import json
def benchmark_dict(r):return {"name":r.name,"median_seconds":r.median_seconds,"min_seconds":r.min_seconds,"max_seconds":r.max_seconds,"samples":[{"seconds":s.seconds,"result_size":s.result_size} for s in r.samples]}
def dumps_benchmark(r):return json.dumps(benchmark_dict(r),sort_keys=True,separators=(",",":"))
