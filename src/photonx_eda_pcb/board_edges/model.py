from dataclasses import dataclass
@dataclass(frozen=True)
class EdgeSegment:
    id:str
    start:tuple[float,float]
    end:tuple[float,float]
@dataclass(frozen=True)
class EdgeLoop:
    id:str
    points:tuple[tuple[float,float],...]
    is_cutout:bool=False
