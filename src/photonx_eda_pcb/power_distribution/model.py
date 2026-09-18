from dataclasses import dataclass,field
@dataclass
class PowerNetEvidence:
    net_id:str
    nominal_voltage:float|None=None
    estimated_resistance_ohm:float|None=None
    estimated_drop_v:float|None=None
    confidence:float=0.0
    assumptions:list[str]=field(default_factory=list)
