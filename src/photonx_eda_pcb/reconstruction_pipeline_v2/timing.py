from time import perf_counter
def timed(fn,*args,**kwargs):
    t=perf_counter();value=fn(*args,**kwargs);return value,perf_counter()-t
