import tracemalloc
def measure_peak_bytes(fn,*args,**kwargs):
    tracemalloc.start()
    try:result=fn(*args,**kwargs);current,peak=tracemalloc.get_traced_memory();return result,peak
    finally:tracemalloc.stop()
