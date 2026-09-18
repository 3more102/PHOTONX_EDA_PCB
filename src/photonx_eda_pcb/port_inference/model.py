from dataclasses import dataclass
@dataclass(frozen=True)
class PortCandidate:
    connector_id:str
    kind:str
    pins:tuple[str,...]
    nets:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
