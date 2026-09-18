from photonx_eda_pcb.regression_baselines import Baseline,compare_baseline
def test_baseline_difference_visible():
    r=compare_baseline(Baseline("b",{"nets":3}),{"nets":4,"new":1})
    assert not r.passed and r.differences==("MISMATCH:nets","NEW:new")
