from dataclasses import dataclass,field
@dataclass
class AnalogAnalysis:
    blocks:list=field(default_factory=list)
    evidence_records:list=field(default_factory=list)
    review_items:list=field(default_factory=list)
