from dataclasses import dataclass
@dataclass(frozen=True)
class ProtectionCandidate:
    component_id:str
    kind:str
    protected_nets:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
    assumptions:tuple[str,...]=()
