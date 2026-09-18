from photonx_eda_pcb.release_manifest import build_release_manifest
from photonx_eda_pcb.release_manifest.compare import compare_release_manifests
def test_release_compare():
    a=build_release_manifest("1","a",[{"path":"x","role":"r","sha256":"a"*64}])
    b=build_release_manifest("2","b",[{"path":"x","role":"r","sha256":"b"*64},{"path":"y","role":"r","sha256":"c"*64}])
    assert compare_release_manifests(a,b)==[("x","modified"),("y","added")]
