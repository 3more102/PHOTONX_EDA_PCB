from dataclasses import dataclass,field
@dataclass(frozen=True)
class AssemblyFinding:
    code:str
    severity:str
    reference:str=""
    message:str=""
@dataclass
class AssemblyDfmReport:
    findings:list[AssemblyFinding]=field(default_factory=list)
    metrics:dict[str,float|int]=field(default_factory=dict)
