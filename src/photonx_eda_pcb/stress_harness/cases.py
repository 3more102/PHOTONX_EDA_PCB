from dataclasses import dataclass
@dataclass(frozen=True)
class StressCase:
    name:str
    size:int
    repetitions:int=1
