from dataclasses import dataclass,field
@dataclass(frozen=True)
class ReportSection:
    name:str
    payload:object
@dataclass
class UnifiedReport:
    title:str
    sections:list[ReportSection]=field(default_factory=list)
