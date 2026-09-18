from photonx_eda_pcb.production_release_profiles import manufacturing_candidate_profile,ReleaseEvidence,evaluate_release_profile
def test_manufacturing_profile_blocks_missing_evidence():
    p=manufacturing_candidate_profile()
    e=ReleaseEvidence({"error":1},{"provenance_coverage":.5,"completeness":.5},1,False,False,2,False,False,False,False)
    d=evaluate_release_profile(p,e)
    assert not d.passed
    assert "TESTS_NOT_PASSED" in d.blockers and "GROUND_TRUTH_FAILED" in d.blockers
