from dataclasses import dataclass, field

@dataclass
class TestPointCandidate:
    object_id:str
    net_id:str|None
    diameter_mm:float
    exposed:bool
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)
