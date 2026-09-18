from dataclasses import dataclass
@dataclass(frozen=True)
class DecouplingGroup:
    power_net:str
    components:tuple[str,...]
    total_capacitance_f:float|None
    bulk_components:tuple[str,...]
    quality_score:float
    confidence:float
