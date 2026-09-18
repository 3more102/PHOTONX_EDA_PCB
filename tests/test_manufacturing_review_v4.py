from photonx_eda_pcb.manufacturing_review import run_manufacturing_review,release_decision
def test_review_blocks_unsupported():
    r=run_manufacturing_review(drc_issues=[],erc_issues=[],unresolved=1,unsupported=2)
    d=release_decision(r)
    assert d["ready"] is False
    assert "UNSUPPORTED_SYNTAX" in d["blockers"]
