from photonx_eda_pcb.milestone_readiness import MilestoneInput,evaluate_phase70
def test_phase70_requires_full_evidence():
    r=evaluate_phase70(MilestoneInput())
    assert not r.passed and "PHASE70_RELEASE_CANDIDATE_BLOCKED" in r.blockers and "PHASE70_TRACEABILITY_LOW" in r.blockers
