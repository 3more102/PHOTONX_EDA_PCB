from dataclasses import dataclass,field
@dataclass(frozen=True)
class QualityCard:
    name:str
    score:float
    status:str
    details:dict=field(default_factory=dict)
@dataclass
class QualityDashboard:
    cards:list[QualityCard]=field(default_factory=list)
    overall_score:float=0.0
