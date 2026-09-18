from dataclasses import dataclass
@dataclass(frozen=True)
class CircuitInstance:
    id:str
    seed:str
    components:tuple[str,...]
    nets:tuple[str,...]
    fingerprint:str
    similarity:float
    differences:tuple[str,...]=()
@dataclass(frozen=True)
class RepeatedCircuitGroup:
    id:str
    instances:tuple[CircuitInstance,...]
    topology_fingerprint:str
    similarity:float
    confidence:float
    evidence:tuple[str,...]=()
