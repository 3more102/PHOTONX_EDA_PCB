from photonx_eda_pcb.workspace_index import build_index
from photonx_eda_pcb.workspace_index.fingerprints import workspace_fingerprint
def test_workspace_fingerprint_deterministic():
    a=build_index([{"path":"b","role":"x"},{"path":"a","role":"y"}])
    b=build_index([{"path":"a","role":"y"},{"path":"b","role":"x"}])
    assert workspace_fingerprint(a)==workspace_fingerprint(b)
