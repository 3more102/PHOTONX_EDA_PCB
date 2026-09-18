from dataclasses import dataclass
@dataclass(frozen=True)
class PlacementDelta:
    reference:str
    distance_mm:float
    rotation_delta_deg:float
    side_match:bool
    code:str="OK"
