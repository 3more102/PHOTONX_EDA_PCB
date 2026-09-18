from photonx_eda_pcb.release_manifest.model import ReleaseArtifact
from photonx_eda_pcb.release_candidate import build_release_candidate,evaluate_release_candidate
from photonx_eda_pcb.release_candidate.fingerprint import candidate_fingerprint
def test_release_candidate():
    c=build_release_candidate("rc1","abc",[ReleaseArtifact("x","report","a"*64)])
    d=evaluate_release_candidate(c)
    assert d.passed and len(candidate_fingerprint(c))==64
