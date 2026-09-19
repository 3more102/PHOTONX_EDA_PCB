from dataclasses import dataclass, field

from ..provenance import Provenance


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
    clearance_mm:float|None=None
    min_thickness_mm:float|None=None
    provenance:Provenance=field(default_factory=Provenance)
