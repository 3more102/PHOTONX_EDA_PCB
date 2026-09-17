from photonx_eda_pcb.quality_gate.thresholds import QualityThresholds
from photonx_eda_pcb.quality_gate.decision import evaluate_gate

def test_quality_gate_pass_and_fail():
    t=QualityThresholds(min_provenance_coverage=.5,min_completeness=.5)
    assert evaluate_gate({'error':0},{'provenance_coverage':.8,'completeness':.9},t).passed
    r=evaluate_gate({'error':1},{'provenance_coverage':.2,'completeness':.9},t)
    assert not r.passed and len(r.findings)>=2
