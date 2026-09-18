from dataclasses import dataclass
@dataclass(frozen=True)
class BiasCandidate:
    component_id:str
    net_id:str
    reference_net:str
    kind:str
    value_ohm:float|None
    confidence:float
