from photonx_eda_pcb.release_manifest import build_release_manifest,validate_release_manifest
from photonx_eda_pcb.release_manifest.signature import manifest_signature
def test_release_manifest():
    m=build_release_manifest("0.3","abc",[{"path":"board.json","role":"report","sha256":"a"*64,"size":10}])
    assert validate_release_manifest(m)==[] and len(manifest_signature(m))==64
