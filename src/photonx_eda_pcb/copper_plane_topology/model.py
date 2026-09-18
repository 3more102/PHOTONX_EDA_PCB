from dataclasses import dataclass,field
@dataclass(frozen=True)
class PlaneIsland:
    id:str
    layer:str
    area_mm2:float
    net_id:str|None=None
    touches:tuple[str,...]=()
@dataclass
class PlaneTopology:
    islands:list[PlaneIsland]=field(default_factory=list)
    adjacency:dict[str,set[str]]=field(default_factory=dict)
