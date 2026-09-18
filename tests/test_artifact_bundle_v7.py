from photonx_eda_pcb.artifact_bundle import build_bundle,bundle_manifest,validate_bundle
from photonx_eda_pcb.artifact_bundle.signature import bundle_signature
def test_artifact_bundle():
    b=build_bundle("release",[{"path":"board.json","role":"report","content":"{}"},{"path":"board.kicad_pcb","role":"design","content":"pcb"}])
    assert validate_bundle(b)==[]
    assert bundle_manifest(b)["name"]=="release"
    assert len(bundle_signature(b))==64
