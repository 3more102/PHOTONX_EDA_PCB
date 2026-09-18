from dataclasses import dataclass
@dataclass(frozen=True)
class ComponentNeighborhood:
    component_id:str
    nets:tuple[str,...]
    neighbors:tuple[str,...]
    degree:int
    kinds:tuple[str,...]=()
