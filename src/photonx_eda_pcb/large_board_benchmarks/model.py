from dataclasses import dataclass
@dataclass(frozen=True)
class BenchmarkScenario:
    name:str
    rows:int
    cols:int
    pitch_mm:float=2.0
    iterations:int=1
