from photonx_eda_pcb.regression_baselines import Baseline,compare_baseline
def test_baseline_tolerance():
    r=compare_baseline(Baseline("b",{"nets":3,"runtime":1.0},{"runtime":.2}),{"nets":3,"runtime":1.1})
    assert r.passed
