from time import perf_counter
class Timer:
    def __init__(self): self.elapsed=0.0; self._start=None
    def __enter__(self): self._start=perf_counter(); return self
    def __exit__(self,*_): self.elapsed=perf_counter()-self._start
