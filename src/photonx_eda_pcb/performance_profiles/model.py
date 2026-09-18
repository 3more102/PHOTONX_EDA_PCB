from dataclasses import dataclass
@dataclass(frozen=True)
class BenchmarkSample:
    seconds:float
    result_size:int|None=None
@dataclass(frozen=True)
class BenchmarkResult:
    name:str
    samples:tuple[BenchmarkSample,...]
    median_seconds:float
    min_seconds:float
    max_seconds:float
