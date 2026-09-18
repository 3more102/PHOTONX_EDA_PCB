from dataclasses import dataclass
@dataclass(frozen=True)
class PinFunctionCandidate:
    connector_id:str
    pin:str
    net_id:str
    function:str
    confidence:float
    evidence:tuple[str,...]=()
@dataclass(frozen=True)
class ResolvedPinFunction:
    connector_id:str
    pin:str
    net_id:str
    function:str|None
    confidence:float
    evidence:tuple[str,...]=()
    conflicts:tuple[str,...]=()
