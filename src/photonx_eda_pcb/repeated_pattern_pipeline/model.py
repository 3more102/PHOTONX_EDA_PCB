from dataclasses import dataclass,field
@dataclass
class RepeatedPatternAnalysis:
    fingerprints:list=field(default_factory=list)
    repeated_groups:list=field(default_factory=list)
    channels:list=field(default_factory=list)
    pattern_matches:list=field(default_factory=list)
    evidence_records:list=field(default_factory=list)
    review_items:list=field(default_factory=list)
