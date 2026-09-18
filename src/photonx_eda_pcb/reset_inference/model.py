from dataclasses import dataclass
@dataclass(frozen=True)
class ResetCandidate:
    net_id:str
    active_low:bool|None
    confidence:float
    fanout:int=0
    evidence:tuple[str,...]=()
