from dataclasses import dataclass
@dataclass(frozen=True)
class SlotFeature:
    id:str
    start:tuple[float,float]
    end:tuple[float,float]
    width_mm:float
    plated:str="unknown"
@dataclass(frozen=True)
class MechanicalHole:
    id:str
    center:tuple[float,float]
    diameter_mm:float
    plated:str="non-plated"
