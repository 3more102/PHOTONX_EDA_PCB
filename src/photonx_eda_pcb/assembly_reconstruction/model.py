from dataclasses import dataclass,field
@dataclass(frozen=True)
class AssemblyComponent:
    reference:str
    center:tuple[float,float]
    rotation:float
    side:str
    footprint:str=""
    value:str=""
    confidence:float=1.0
@dataclass
class AssemblyView:
    components:list[AssemblyComponent]=field(default_factory=list)
    evidence:list[str]=field(default_factory=list)
