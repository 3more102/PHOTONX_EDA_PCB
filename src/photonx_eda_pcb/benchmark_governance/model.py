from dataclasses import dataclass
@dataclass(frozen=True)
class BenchmarkPolicy:
    name:str
    max_regression_ratio:float=1.25
    min_pair_reduction:float=0.5
    max_peak_memory_bytes:int|None=None
@dataclass(frozen=True)
class BenchmarkDecision:
    name:str
    passed:bool
    blockers:tuple[str,...]=()
    evidence:dict|None=None
