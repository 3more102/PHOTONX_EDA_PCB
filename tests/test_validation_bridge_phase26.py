from photonx_eda_pcb.validation_bridge import normalize_issues,unified_summary
from photonx_eda_pcb.validation_bridge.quality_gate import counts_for_quality_gate
def test_validation_bridge():
    x=normalize_issues({"drc":[{"code":"C","severity":"error","message":"bad"}],"legacy":["OLD"]})
    assert len(x)==2 and unified_summary(x)["total"]==2
    assert counts_for_quality_gate(x)=={"error":1,"warning":1}
