from photonx_eda_pcb.evidence_consistency import ClaimObservation,analyze_consistency
def test_independent_agreement_increases_confidence():
    items=[ClaimObservation("N1","name","GND","ipc356",.8,"electrical"),ClaimObservation("N1","name","GND","netlist",.8,"cad")]
    r=analyze_consistency(items)
    assert r.consensus[("N1","name")]["confidence"]>.9
    assert not [x for x in r.findings if x.code=="EVIDENCE_CONFLICT"]
