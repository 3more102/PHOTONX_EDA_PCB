from dataclasses import dataclass
@dataclass(frozen=True)
class SupplyDomain:
    name:str
    supply_nets:tuple[str,...]
    ground_nets:tuple[str,...]
    components:tuple[str,...]
    voltage:float|None
    confidence:float
