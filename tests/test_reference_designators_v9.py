from photonx_eda_pcb.reference_designators.model import ReferenceCandidate
from photonx_eda_pcb.reference_designators import resolve_reference,validate_reference
def test_reference_resolution():
    r=resolve_reference("c1",[ReferenceCandidate("c1","R3",.8,"silk"),ReferenceCandidate("c1","R7",.99,"bom")])
    assert r.reference=="R7" and r.conflicts==("R3",)
    assert validate_reference(r.reference)==[]
