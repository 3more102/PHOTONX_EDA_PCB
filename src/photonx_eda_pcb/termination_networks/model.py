from dataclasses import dataclass
@dataclass(frozen=True)
class TerminationCandidate:
    component_id:str
    kind:str
    nets:tuple[str,...]
    value_ohm:float|None
    confidence:float
    evidence:tuple[str,...]=()
