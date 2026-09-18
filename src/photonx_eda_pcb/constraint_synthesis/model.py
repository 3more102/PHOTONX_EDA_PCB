from dataclasses import dataclass,field
@dataclass(frozen=True)
class ConstraintCandidate:
    net_id:str
    min_width_mm:float|None=None
    clearance_mm:float|None=None
    target_length_mm:float|None=None
    length_tolerance_mm:float|None=None
    diff_pair_gap_mm:float|None=None
    confidence:float=0.0
    evidence:tuple[str,...]=()
@dataclass
class ConstraintSet:
    constraints:list[ConstraintCandidate]=field(default_factory=list)
