from photonx_eda_pcb.evidence_fusion import EvidenceItem,fuse_evidence,validate_fused
def test_independent_evidence_increases_confidence():
    f=fuse_evidence([EvidenceItem("gerber","pad",.6,"geometry"),EvidenceItem("mask","pad",.7,"mask")])
    assert f.confidence>.7
    assert validate_fused(f)==[]
def test_correlated_group_not_double_counted():
    f=fuse_evidence([EvidenceItem("a","x",.5,"same"),EvidenceItem("b","x",.6,"same")])
    assert f.confidence==.6
