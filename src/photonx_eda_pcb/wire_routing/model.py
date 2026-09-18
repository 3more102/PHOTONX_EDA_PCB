from dataclasses import dataclass
@dataclass(frozen=True)
class WireRoute:
    net_id:str
    points:tuple[tuple[float,float],...]
    style:str="manhattan"
    confidence:float=1.0
