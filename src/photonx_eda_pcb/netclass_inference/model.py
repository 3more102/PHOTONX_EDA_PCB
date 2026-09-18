from dataclasses import dataclass
@dataclass(frozen=True)
class NetClassCandidate:
    net_id:str
    class_name:str
    confidence:float
    evidence:tuple[str,...]=()
