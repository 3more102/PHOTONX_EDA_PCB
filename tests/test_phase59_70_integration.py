from photonx_eda_pcb.evidence_consistency import ClaimObservation,analyze_consistency
from photonx_eda_pcb.traceability_matrix import build_traceability_matrix
from photonx_eda_pcb.traceability_matrix.coverage import traceability_coverage
from photonx_eda_pcb.milestone_readiness import MilestoneInput,evaluate_phase70
def test_evidence_to_phase70_readiness_flow():
    c=analyze_consistency([ClaimObservation("N1","name","GND","ipc",.9,"a"),ClaimObservation("N1","name","GND","cad",.8,"b")])
    t=build_traceability_matrix([{"claim_id":"N1:name","source_ids":["ipc","cad"],"artifact_ids":["board"],"review_ids":["r"],"object_ids":["N1"],"confidence":.98}])
    ready=evaluate_phase70(MilestoneInput(True,True,True,True,True,True,sum(x.severity=="error" for x in c.findings),0,traceability_coverage(t)["source_coverage"],1.0))
    assert ready.passed
