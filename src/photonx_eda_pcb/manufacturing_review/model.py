from dataclasses import dataclass,field
@dataclass(frozen=True)
class ReviewFinding:
    code:str
    severity:str
    message:str
    object_id:str|None=None
@dataclass
class ReviewReport:
    findings:list[ReviewFinding]=field(default_factory=list)
    metrics:dict[str,float|int]=field(default_factory=dict)
