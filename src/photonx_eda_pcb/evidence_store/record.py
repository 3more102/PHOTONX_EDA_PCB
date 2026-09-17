from dataclasses import dataclass
@dataclass(frozen=True)
class EvidenceRecord:
    id:str
    kind:str
    source:str
    detail:str
    confidence:float
    object_id:str|None=None
    def __post_init__(self):
        if not 0.0<=self.confidence<=1.0: raise ValueError("confidence outside [0,1]")
