from photonx_eda_pcb.reference_designators.model import ResolvedReference
from photonx_eda_pcb.component_identity.model import ResolvedIdentity
from photonx_eda_pcb.semantic_consistency import analyze_semantic_consistency
def test_duplicate_reference_and_identity_conflict():
    refs=[ResolvedReference("a","R1",.9),ResolvedReference("b","R1",.8)]
    ids=[ResolvedIdentity("a","resistor","10k",None,None,.8,(),("1k",))]
    r=analyze_semantic_consistency(ids,refs)
    codes={x.code for x in r.findings}
    assert "REFERENCE_DUPLICATE" in codes and "IDENTITY_CONFLICT" in codes
