from photonx_eda_pcb.ground_truth_matrix import GroundTruthCase,compare_case
def test_ground_truth_mismatch():
    r=compare_case(GroundTruthCase("a",{"nets":10},{"nets":9},{}))
    assert not r.passed and r.mismatches==("MISMATCH:nets",)
