from photonx_eda_pcb.evidence_consistency import ClaimObservation,analyze_consistency,validate_consistency_report
from photonx_eda_pcb.evidence_consistency.metrics import consistency_metrics
def test_conflicting_independent_claims_surface():
    items=[ClaimObservation("U1","value","10k","bom",.9,"bom"),ClaimObservation("U1","value","1k","marking",.85,"marking")]
    r=analyze_consistency(items,.1)
    assert any(x.code=="EVIDENCE_CONFLICT" for x in r.findings)
    assert consistency_metrics(r)["conflicts"]==1
    assert validate_consistency_report(r)==[]
