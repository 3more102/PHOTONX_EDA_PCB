from photonx_eda_pcb.return_path.vias import return_via_penalty
def test_return_via_penalty():
    assert return_via_penalty(2,2)==0.0
    assert return_via_penalty(2,0)==1.0
