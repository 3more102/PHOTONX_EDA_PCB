from dataclasses import dataclass
@dataclass(frozen=True)
class FuseCandidate:
    component_id:str
    nets:tuple[str,...]
    resettable:bool|None
    confidence:float
    evidence:tuple[str,...]=()
