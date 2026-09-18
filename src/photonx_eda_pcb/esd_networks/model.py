from dataclasses import dataclass
@dataclass(frozen=True)
class EsdNetwork:
    interface_net:str
    protection_components:tuple[str,...]
    ground_nets:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
