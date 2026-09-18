from dataclasses import dataclass,field
@dataclass(frozen=True)
class TestabilityFinding:
    code:str
    severity:str
    object_id:str
    message:str
@dataclass
class TestabilityReport:
    findings:list[TestabilityFinding]=field(default_factory=list)
    metrics:dict[str,float|int]=field(default_factory=dict)
