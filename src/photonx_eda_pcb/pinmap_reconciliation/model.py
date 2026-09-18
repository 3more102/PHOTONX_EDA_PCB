from dataclasses import dataclass,field
@dataclass(frozen=True)
class PinMapIssue:
    code:str
    pin:str
    expected:str=""
    observed:str=""
@dataclass
class PinMapReport:
    component_id:str
    issues:list[PinMapIssue]=field(default_factory=list)
    matched:int=0
    total:int=0
