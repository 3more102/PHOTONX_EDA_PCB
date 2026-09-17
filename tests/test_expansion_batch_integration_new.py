from photonx_eda_pcb.copper_solver.model import ContactEdge
from photonx_eda_pcb.copper_solver.solver import solve_connectivity
from photonx_eda_pcb.quality_gate.decision import evaluate_gate
from photonx_eda_pcb.quality_gate.thresholds import QualityThresholds

def test_solver_output_can_feed_quality_metrics():
    r=solve_connectivity(['a','b'],[ContactEdge('a','b')])
    completeness=1.0 if r.groups else 0.0
    g=evaluate_gate({'error':len([d for d in r.diagnostics if d.get('severity')=='error'])},{'completeness':completeness,'provenance_coverage':1.0},QualityThresholds())
    assert g.passed
