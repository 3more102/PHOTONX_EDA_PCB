from dataclasses import dataclass,field
@dataclass
class CurrentCapacityEstimate:
    net_id:str
    width_mm:float
    copper_um:float
    temperature_rise_c:float
    estimated_current_a:float
    confidence:float
    assumptions:list[str]=field(default_factory=list)
