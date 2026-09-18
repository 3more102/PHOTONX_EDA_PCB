from dataclasses import dataclass,field
@dataclass(frozen=True)
class LayoutPosition:
    object_id:str
    x:float
    y:float
    layer:int=0
@dataclass
class LayoutResult:
    positions:dict[str,LayoutPosition]=field(default_factory=dict)
    width:float=0.0
    height:float=0.0
