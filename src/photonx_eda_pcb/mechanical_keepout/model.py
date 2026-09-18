from dataclasses import dataclass
@dataclass(frozen=True)
class KeepoutRegion:
    id:str
    bounds:tuple[float,float,float,float]
    kind:str="component"
    source:str=""
@dataclass(frozen=True)
class KeepoutViolation:
    keepout_id:str
    object_id:str
    kind:str
