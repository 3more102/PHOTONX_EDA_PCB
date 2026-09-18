from photonx_eda_pcb.ground_truth_matrix import GroundTruthCase,compare_case,summarize_results
def test_ground_truth_with_tolerance():
    r=compare_case(GroundTruthCase("a",{"nets":10,"width":1.0},{"nets":10,"width":1.02},{"width":.05}))
    assert r.passed and summarize_results([r])["pass_rate"]==1.0
