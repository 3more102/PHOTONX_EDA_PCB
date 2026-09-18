from dataclasses import dataclass,field
@dataclass(frozen=True)
class HealthMetric:
    name:str
    score:float
    weight:float=1.0
    details:str=""
@dataclass
class ProjectHealth:
    metrics:list[HealthMetric]=field(default_factory=list)
    score:float=0.0
