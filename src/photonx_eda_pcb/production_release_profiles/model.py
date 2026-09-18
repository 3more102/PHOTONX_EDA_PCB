from dataclasses import dataclass
from photonx_eda_pcb.quality_gate.thresholds import QualityThresholds
@dataclass(frozen=True)
class ReleaseProfile:
    name:str
    thresholds:QualityThresholds
    require_tests:bool=False
    require_determinism:bool=False
    require_zero_unsupported:bool=False
    require_provenance_complete:bool=False
    require_review_closed:bool=False
    require_roundtrip:bool=False
    require_ground_truth:bool=False
@dataclass(frozen=True)
class ReleaseEvidence:
    issue_counts:dict
    metrics:dict
    regression_failures:int=0
    tests_passed:bool=False
    deterministic:bool=False
    unsupported_critical:int=0
    provenance_complete:bool=False
    mandatory_reviews_closed:bool=False
    roundtrip_passed:bool=False
    ground_truth_passed:bool=False
@dataclass(frozen=True)
class ReleaseDecision:
    profile:str
    passed:bool
    blockers:tuple[str,...]
    warnings:tuple[str,...]
