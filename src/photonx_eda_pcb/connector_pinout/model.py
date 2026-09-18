from dataclasses import dataclass,field
@dataclass(frozen=True)
class PinoutCandidate:
    pin_id:str
    net_id:str|None
    role:str
    confidence:float
    evidence:tuple[str,...]=()
@dataclass
class ConnectorPinout:
    component_id:str
    pins:list[PinoutCandidate]=field(default_factory=list)
