from photonx_eda_pcb.component_identity.model import IdentityCandidate
from photonx_eda_pcb.component_identity import resolve_identity
def test_identity_conflict_visible():
    c=[IdentityCandidate("X","resistor","10k",None,None,.9,"bom"),IdentityCandidate("X","resistor","1k",None,None,.8,"marking")]
    r=resolve_identity("X",c)
    assert r.value=="10k" and "1k" in r.conflicts
