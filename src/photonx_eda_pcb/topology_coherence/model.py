from dataclasses import dataclass,field
@dataclass(frozen=True)
class TopologyFinding:
    code:str
    severity:str
    subject:str
    detail:str
@dataclass
class TopologyCoherenceReport:
    findings:list[TopologyFinding]=field(default_factory=list)
