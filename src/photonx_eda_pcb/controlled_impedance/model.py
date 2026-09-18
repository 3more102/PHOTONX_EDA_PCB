from dataclasses import dataclass
@dataclass(frozen=True)
class ImpedanceConstraint:
    net_id:str
    target_ohms:float
    tolerance_ohms:float=10.0
    mode:str="single-ended"
@dataclass(frozen=True)
class ImpedanceCheck:
    net_id:str
    estimate_ohms:float|None
    target_ohms:float
    error_ohms:float|None
    passed:bool|None
    confidence:float
