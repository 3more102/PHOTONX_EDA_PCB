from dataclasses import dataclass
@dataclass(frozen=True)
class NetNameCandidate:
    net_id:str
    name:str
    confidence:float
    source:str
    evidence:str=""
@dataclass(frozen=True)
class ResolvedNetName:
    net_id:str
    name:str|None
    confidence:float
    sources:tuple[str,...]=()
    conflicts:tuple[str,...]=()
