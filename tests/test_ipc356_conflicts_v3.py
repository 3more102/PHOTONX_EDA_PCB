from photonx_eda_pcb.ipc356.evidence import IpcNetEvidence
from photonx_eda_pcb.ipc356.conflicts import pad_net_conflicts
def test_conflict_detection():
    e=[IpcNetEvidence("P1","A",None,None,.7),IpcNetEvidence("P1","B",None,None,.7)]
    assert pad_net_conflicts(e)=={"P1":["A","B"]}
