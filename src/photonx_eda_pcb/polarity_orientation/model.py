from dataclasses import dataclass
@dataclass(frozen=True)
class PolarityCandidate:
    component_id:str
    positive_pin:str|None
    negative_pin:str|None
    confidence:float
    evidence:tuple[str,...]=()
@dataclass(frozen=True)
class OrientationCandidate:
    component_id:str
    rotation_deg:float
    pin1:str|None
    confidence:float
    evidence:tuple[str,...]=()
