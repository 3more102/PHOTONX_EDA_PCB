from dataclasses import dataclass,field
@dataclass(frozen=True)
class Baseline:
    id:str
    metrics:dict[str,object]
    tolerances:dict[str,float]=field(default_factory=dict)
@dataclass(frozen=True)
class BaselineResult:
    id:str
    passed:bool
    differences:tuple[str,...]=()
