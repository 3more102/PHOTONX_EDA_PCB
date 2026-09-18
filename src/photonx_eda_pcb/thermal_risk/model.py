from dataclasses import dataclass
@dataclass(frozen=True)
class ThermalObservation:
    object_id:str
    power_w:float|None=None
    copper_area_mm2:float|None=None
    thermal_vias:int=0
    ambient_c:float|None=None
    source:str="inferred"
@dataclass(frozen=True)
class ThermalRisk:
    object_id:str
    risk:float
    confidence:float
    evidence:tuple[str,...]=()
    assumptions:tuple[str,...]=()
