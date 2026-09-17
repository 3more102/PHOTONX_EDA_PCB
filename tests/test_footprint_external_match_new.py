from photonx_eda_pcb.footprint_reconstruction.external_match import match_external

def test_external_reference_match():
    assert match_external('r1',[{'reference':'R1','value':'330R'}])['value']=='330R'
