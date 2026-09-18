from dataclasses import dataclass,field
@dataclass(frozen=True)
class PowerNode:
    id:str
    kind:str
    voltage:float|None=None
@dataclass(frozen=True)
class PowerEdge:
    source:str
    target:str
    relation:str="feeds"
    confidence:float=.5
@dataclass
class PowerTree:
    nodes:dict[str,PowerNode]=field(default_factory=dict)
    edges:list[PowerEdge]=field(default_factory=list)
