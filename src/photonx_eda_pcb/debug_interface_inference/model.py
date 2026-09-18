from dataclasses import dataclass
@dataclass(frozen=True)
class DebugInterfaceCandidate:
    protocol:str
    nets:tuple[str,...]
    components:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
