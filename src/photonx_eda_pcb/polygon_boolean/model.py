from dataclasses import dataclass
@dataclass(frozen=True)
class PolygonRecord:
    id:str
    points:tuple[tuple[float,float],...]
    source:str|None=None
