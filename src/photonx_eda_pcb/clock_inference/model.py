from dataclasses import dataclass
@dataclass(frozen=True)
class ClockCandidate:
    net_id:str
    confidence:float
    evidence:tuple[str,...]=()
    fanout:int=0
    frequency_hz:float|None=None
