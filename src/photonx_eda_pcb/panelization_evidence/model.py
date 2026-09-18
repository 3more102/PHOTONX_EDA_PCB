from dataclasses import dataclass,field
@dataclass(frozen=True)
class RepeatedBoard:
    id:str
    bounds:tuple[float,float,float,float]
@dataclass
class PanelHypothesis:
    boards:list[RepeatedBoard]=field(default_factory=list)
    rail_width_mm:float|None=None
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)
