from dataclasses import dataclass
@dataclass(frozen=True)
class BusCandidate:
    name:str
    net_ids:tuple[str,...]
    indices:tuple[int,...]
    width:int
    confidence:float
    evidence:tuple[str,...]=()
