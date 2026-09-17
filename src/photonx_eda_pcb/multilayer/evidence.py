from dataclasses import dataclass
@dataclass(frozen=True)
class LayerConnectionEvidence:
    a:str
    b:str
    kind:str
    confidence:float
    def __post_init__(self):
        if not 0<=self.confidence<=1: raise ValueError("confidence outside [0,1]")
