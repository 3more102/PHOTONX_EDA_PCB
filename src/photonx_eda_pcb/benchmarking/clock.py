from time import perf_counter_ns
def now_ns():return perf_counter_ns()
def elapsed_seconds(start_ns,end_ns):return (end_ns-start_ns)/1_000_000_000.0
