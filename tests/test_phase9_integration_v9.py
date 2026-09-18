from photonx_eda_pcb.source_changes import SourceState,compare_sources
from photonx_eda_pcb.board_variants.model import VariantDefinition,VariantComponent
from photonx_eda_pcb.net_naming.model import NetNameCandidate
from photonx_eda_pcb.net_naming import resolve_net_name
from photonx_eda_pcb.reference_designators.model import ReferenceCandidate
from photonx_eda_pcb.reference_designators import resolve_reference
from photonx_eda_pcb.component_identity.model import IdentityCandidate
from photonx_eda_pcb.component_identity import resolve_identity
def test_phase9_semantic_recovery_flow():
    assert compare_sources([SourceState("a","a"*64)],[SourceState("a","b"*64)]).changes
    assert VariantDefinition("A",{"R1":VariantComponent("R1",False)}).components["R1"].fitted is False
    assert resolve_net_name("n",[NetNameCandidate("n","GND",.9,"ipc356")]).name=="GND"
    assert resolve_reference("c",[ReferenceCandidate("c","R1",.9,"bom")]).reference=="R1"
    assert resolve_identity("c",[IdentityCandidate("c","resistor","10k","R_0603",None,.9,"bom")]).value=="10k"
