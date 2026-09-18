from dataclasses import dataclass,field
@dataclass(frozen=True)
class FidelitySection:
    name:str
    equal:bool
    left_count:int
    right_count:int
    weight:float=1.0
@dataclass
class FidelityReport:
    sections:list[FidelitySection]=field(default_factory=list)
    score:float=0.0
    exact:bool=False
