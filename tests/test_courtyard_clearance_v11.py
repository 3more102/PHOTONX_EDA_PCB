from photonx_eda_pcb.assembly_dfm.courtyard import courtyard_clearance
def test_courtyard_clearance():
    assert courtyard_clearance((0,0,1,1),(2,0,3,1))==1.0
    assert courtyard_clearance((0,0,2,2),(1,1,3,3))==0.0
