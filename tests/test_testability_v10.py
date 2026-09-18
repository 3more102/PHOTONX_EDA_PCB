from photonx_eda_pcb.testpoints.model import TestPointCandidate
from photonx_eda_pcb.testability_analysis import analyze_testability,validate_testability
from photonx_eda_pcb.testability_analysis.score import testability_score
def test_testability_metrics():
    t=[TestPointCandidate("tp1","n1",1.0,True,.9,[]),TestPointCandidate("tp2","n2",.4,True,.9,[])]
    r=analyze_testability(["n1","n2"],t,min_net_coverage=.8)
    assert r.metrics["net_test_coverage"]==.5
    assert testability_score(r)<1
    assert validate_testability(r)==[]
