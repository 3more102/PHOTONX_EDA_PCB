from dataclasses import dataclass
@dataclass(frozen=True)
class Endpoint:
    component_id:str
    pin:str|None
    role:str
@dataclass(frozen=True)
class SerialLink:
    protocol:str
    nets:tuple[str,...]
    endpoints:tuple[Endpoint,...]
    confidence:float
    evidence:tuple[str,...]=()
