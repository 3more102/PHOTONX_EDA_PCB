from dataclasses import dataclass
@dataclass(frozen=True)
class Placement:
    reference:str
    x:float
    y:float
    rotation:float=0.0
    side:str="top"
    value:str=""
    footprint:str=""
