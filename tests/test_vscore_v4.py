from photonx_eda_pcb.panelization_evidence.vscore import vscore_candidate
def test_vscore_candidate():
    assert vscore_candidate(100,100,90)>.9
