from dataclasses import dataclass,field
@dataclass(frozen=True)
class SemanticFinding:
    code:str
    severity:str
    object_id:str
    detail:str
@dataclass
class SemanticConsistencyReport:
    findings:list[SemanticFinding]=field(default_factory=list)
