from dataclasses import dataclass
@dataclass(frozen=True)
class NetNameCandidate:
    net_id:str
    name:str
    confidence:float
    source:str
    rationale:str=""
    def __post_init__(self):
        if not 0<=self.confidence<=1: raise ValueError("confidence outside [0,1]")
