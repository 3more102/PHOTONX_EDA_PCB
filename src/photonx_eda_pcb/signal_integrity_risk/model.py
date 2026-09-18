from dataclasses import dataclass,field
@dataclass
class SignalIntegrityRisk:
    net_id:str
    score:float
    level:str
    factors:dict[str,float]=field(default_factory=dict)
    confidence:float=0.0
