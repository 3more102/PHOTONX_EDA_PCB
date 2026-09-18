from dataclasses import dataclass
@dataclass(frozen=True)
class IdentityCandidate:
    component_id:str
    kind:str
    value:str|None
    footprint:str|None
    mpn:str|None
    confidence:float
    source:str
@dataclass(frozen=True)
class ResolvedIdentity:
    component_id:str
    kind:str|None
    value:str|None
    footprint:str|None
    mpn:str|None
    confidence:float
    sources:tuple[str,...]=()
    conflicts:tuple[str,...]=()
