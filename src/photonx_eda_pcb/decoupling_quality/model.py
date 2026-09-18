from dataclasses import dataclass
@dataclass(frozen=True)
class DecouplingObservation:
    component_id:str
    power_net:str
    ground_net:str
    distance_mm:float|None=None
    capacitance_f:float|None=None
@dataclass(frozen=True)
class DecouplingQuality:
    component_id:str
    power_net:str
    score:float
    confidence:float
    evidence:tuple[str,...]=()
