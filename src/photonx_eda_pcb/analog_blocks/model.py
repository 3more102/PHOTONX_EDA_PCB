from dataclasses import dataclass
@dataclass(frozen=True)
class AnalogBlockCandidate:
    id:str
    kind:str
    components:tuple[str,...]
    nets:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
    parameters:tuple[tuple[str,object],...]=()
    assumptions:tuple[str,...]=()
