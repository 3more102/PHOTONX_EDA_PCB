from photonx_eda_pcb.release_candidate import build_release_candidate,evaluate_release_candidate
def test_empty_candidate_blocks():
    d=evaluate_release_candidate(build_release_candidate("rc","",[]))
    assert not d.passed and "RC_COMMIT_MISSING" in d.blockers and "RC_ARTIFACTS_EMPTY" in d.blockers
