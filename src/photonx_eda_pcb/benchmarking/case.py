from dataclasses import dataclass,field
from typing import Callable
@dataclass(frozen=True)
class BenchmarkCase:
    name:str;fn:Callable;iterations:int=1;warmup:int=0;metadata:dict=field(default_factory=dict)
    def validate(self):
        if self.iterations<1:raise ValueError('iterations must be >= 1')
        if self.warmup<0:raise ValueError('warmup must be >= 0')
        return True
