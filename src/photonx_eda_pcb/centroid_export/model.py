from dataclasses import dataclass
@dataclass(frozen=True)
class CentroidRecord:
    reference:str
    x_mm:float
    y_mm:float
    rotation_deg:float
    side:str
    footprint:str=""
    value:str=""
