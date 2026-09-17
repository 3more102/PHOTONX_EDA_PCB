from dataclasses import dataclass, field
@dataclass
class StableIdFactory:
    prefix:str
    _next:int=field(default=0, init=False)
    def new(self)->str:
        value=f"{self.prefix}{self._next}"; self._next+=1; return value
    def reserve(self, count:int)->list[str]:
        if count<0: raise ValueError("count must be non-negative")
        return [self.new() for _ in range(count)]
