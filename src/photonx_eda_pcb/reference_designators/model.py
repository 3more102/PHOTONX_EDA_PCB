from dataclasses import dataclass
@dataclass(frozen=True)
class ReferenceCandidate:
    component_id:str
    reference:str
    confidence:float
    source:str
@dataclass(frozen=True)
class ResolvedReference:
    component_id:str
    reference:str|None
    confidence:float
    sources:tuple[str,...]=()
    conflicts:tuple[str,...]=()
