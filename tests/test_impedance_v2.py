from photonx_eda_pcb.impedance_evidence import microstrip_estimate,evidence_confidence
def test_impedance_is_reasonable():
    z=microstrip_estimate(.3,.2,4.2)
    assert 20<z<150
    assert evidence_confidence(True,True,True,True)==1.0
