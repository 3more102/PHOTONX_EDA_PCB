from dataclasses import dataclass
@dataclass(frozen=True)
class EmcCandidate:
    component_id:str
    kind:str
    nets:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
