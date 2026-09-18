from dataclasses import dataclass,field
@dataclass(frozen=True)
class RiskItem:
    domain:str
    code:str
    score:float
    severity:str="warning"
@dataclass
class ManufacturingRisk:
    items:list[RiskItem]=field(default_factory=list)
    score:float=0.0
    level:str="none"
