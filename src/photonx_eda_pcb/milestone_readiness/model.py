from dataclasses import dataclass,field
@dataclass
class MilestoneInput:
    release_candidate_passed:bool=False
    manufacturing_audit_passed:bool=False
    change_control_passed:bool=False
    compatibility_freeze_passed:bool=False
    deterministic_replay_passed:bool=False
    benchmark_governance_passed:bool=False
    evidence_consistency_errors:int=0
    semantic_errors:int=0
    traceability_coverage:float=0.0
    roundtrip_fidelity:float=0.0
@dataclass(frozen=True)
class MilestoneReadiness:
    phase:int
    passed:bool
    score:float
    blockers:tuple[str,...]
    warnings:tuple[str,...]
