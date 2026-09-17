from dataclasses import dataclass
@dataclass
class CacheStats:
    hits:int=0
    misses:int=0
    def hit(self): self.hits+=1
    def miss(self): self.misses+=1
    @property
    def requests(self): return self.hits+self.misses
    @property
    def hit_rate(self): return 0.0 if not self.requests else self.hits/self.requests
