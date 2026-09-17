from photonx_eda_pcb.copper_solver.evidence import contact_confidence,contact_reason

def test_contact_evidence_scoring():
    assert contact_confidence(True,True,True,True)==1.0
    assert contact_confidence(True,False,False,False)==.45
    assert contact_reason(geometry=True,plating=False)=='geometry'
