from dataclasses import dataclass,field
@dataclass
class BenchmarkResult:
    name:str;durations:list[float]=field(default_factory=list);metadata:dict=field(default_factory=dict);error:str|None=None
    @property
    def ok(self):return self.error is None
    @property
    def count(self):return len(self.durations)
