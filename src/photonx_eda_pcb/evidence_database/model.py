from dataclasses import dataclass
@dataclass(frozen=True)
class EvidenceRecord:
    id:str
    object_id:str
    kind:str
    confidence:float
    source:str=""
    detail:str=""
    group:str=""
