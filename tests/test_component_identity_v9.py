from photonx_eda_pcb.component_identity.model import IdentityCandidate
from photonx_eda_pcb.component_identity import resolve_identity,validate_identity
def test_identity_combines_fields_and_skips_unknown_kind():
    c=[IdentityCandidate("R1","unknown","10k","R_0603",None,.99,"bom"),IdentityCandidate("R1","resistor",None,None,None,.8,"geometry")]
    r=resolve_identity("R1",c)
    assert r.kind=="resistor" and r.value=="10k" and r.footprint=="R_0603"
    assert validate_identity(r)==[]
