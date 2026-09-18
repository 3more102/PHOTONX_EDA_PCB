from dataclasses import dataclass,field
@dataclass(frozen=True)
class ArchitectureFinding:
    code:str
    severity:str
    subject:str
    detail:str
@dataclass
class ArchitectureAudit:
    findings:list[ArchitectureFinding]=field(default_factory=list)
    metrics:dict[str,int|float]=field(default_factory=dict)
