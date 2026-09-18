from dataclasses import dataclass,field
@dataclass(frozen=True)
class AutoLayoutPlan:
    page_id:str
    component_ids:tuple[str,...]
    net_ids:tuple[str,...]
    x_step:float=30.0
    y_step:float=20.0
    grid:float=2.54
@dataclass
class AutoLayoutResult:
    page_id:str
    positions:dict[str,tuple[float,float]]=field(default_factory=dict)
    routes:list[object]=field(default_factory=list)
    crossings:int=0
