from .model import MilestoneReadiness
def evaluate_phase70(x):
    blockers=[];warnings=[];checks=[
      ("RELEASE_CANDIDATE",x.release_candidate_passed),
      ("MANUFACTURING_AUDIT",x.manufacturing_audit_passed),
      ("CHANGE_CONTROL",x.change_control_passed),
      ("COMPATIBILITY_FREEZE",x.compatibility_freeze_passed),
      ("DETERMINISTIC_REPLAY",x.deterministic_replay_passed),
      ("BENCHMARK_GOVERNANCE",x.benchmark_governance_passed),
    ]
    for name,ok in checks:
        if not ok:blockers.append("PHASE70_"+name+"_BLOCKED")
    if x.evidence_consistency_errors:blockers.append("PHASE70_EVIDENCE_CONSISTENCY_ERRORS")
    if x.semantic_errors:blockers.append("PHASE70_SEMANTIC_ERRORS")
    if x.traceability_coverage<.95:blockers.append("PHASE70_TRACEABILITY_LOW")
    if x.roundtrip_fidelity<.95:blockers.append("PHASE70_FIDELITY_LOW")
    score_parts=[1.0 if ok else 0.0 for _,ok in checks]+[max(0,min(1,x.traceability_coverage)),max(0,min(1,x.roundtrip_fidelity)),1.0 if not x.evidence_consistency_errors else 0.0,1.0 if not x.semantic_errors else 0.0]
    score=round(sum(score_parts)/len(score_parts),6)
    if score<1 and not blockers:warnings.append("PHASE70_NOT_FULL_SCORE")
    return MilestoneReadiness(70,not blockers,score,tuple(sorted(set(blockers))),tuple(sorted(set(warnings))))
