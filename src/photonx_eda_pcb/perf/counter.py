from collections import Counter
class CounterSet:
    def __init__(self): self._counter=Counter()
    def inc(self,name,n=1): self._counter[str(name)]+=n
    def snapshot(self): return dict(sorted(self._counter.items()))
