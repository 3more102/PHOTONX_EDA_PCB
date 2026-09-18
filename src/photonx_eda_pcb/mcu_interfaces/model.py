from dataclasses import dataclass
@dataclass(frozen=True)
class McuInterface:
    component_id:str
    protocol:str
    nets:tuple[str,...]
    pins:tuple[tuple[str,str],...]
    peers:tuple[str,...]
    confidence:float
