from dataclasses import dataclass,field
@dataclass(frozen=True)
class AuditCheck:
    name:str
    passed:bool
    details:str=""
@dataclass
class AuditReport:
    checks:list[AuditCheck]=field(default_factory=list)
    metadata:dict[str,object]=field(default_factory=dict)
