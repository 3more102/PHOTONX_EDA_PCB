from dataclasses import dataclass,field
@dataclass(frozen=True)
class PeripheralBinding:
    component_id:str
    protocol:str
    nets:tuple[str,...]
    peer_components:tuple[str,...]
    role:str
    confidence:float
    evidence:tuple[str,...]=()
@dataclass
class PeripheralMap:
    bindings:list[PeripheralBinding]=field(default_factory=list)
