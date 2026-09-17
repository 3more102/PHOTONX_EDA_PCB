from dataclasses import dataclass, field

@dataclass(frozen=True)
class ZoneIsland:
    id:str
    polygon:tuple[tuple[float,float],...]

@dataclass
class Zone:
    id:str
    layer:str
    net_id:str|None=None
    islands:list[ZoneIsland]=field(default_factory=list)
    clearance_mm:float=0.2
    min_thickness_mm:float=0.2
