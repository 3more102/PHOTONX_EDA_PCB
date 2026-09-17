from dataclasses import dataclass, field

@dataclass(frozen=True)
class ThermalSpoke:
    angle_deg:float
    width_mm:float
    length_mm:float

@dataclass
class ThermalRelief:
    pad_id:str
    zone_id:str
    spokes:list[ThermalSpoke]=field(default_factory=list)
    gap_mm:float=0.2
    inferred:bool=True
