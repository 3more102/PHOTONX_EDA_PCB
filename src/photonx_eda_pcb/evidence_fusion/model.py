from dataclasses import dataclass,field
@dataclass(frozen=True)
class EvidenceItem:
    source:str
    claim:str
    confidence:float
    independent_group:str|None=None
@dataclass
class FusedEvidence:
    claim:str
    confidence:float
    sources:list[str]=field(default_factory=list)
    groups:list[str]=field(default_factory=list)
