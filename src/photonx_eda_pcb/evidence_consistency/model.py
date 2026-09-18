from dataclasses import dataclass,field
@dataclass(frozen=True)
class ClaimObservation:
    subject_id:str
    field:str
    value:object
    source:str
    confidence:float
    independent_group:str|None=None
@dataclass(frozen=True)
class ConsistencyFinding:
    code:str
    severity:str
    subject_id:str
    field:str
    detail:str
@dataclass
class ConsistencyReport:
    findings:list[ConsistencyFinding]=field(default_factory=list)
    consensus:dict[tuple[str,str],dict]=field(default_factory=dict)
