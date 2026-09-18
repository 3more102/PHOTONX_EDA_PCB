from photonx_eda_pcb.solder_mask import reconstruct_mask_openings,validate_mask_openings
def test_mask_reconstruction():
    pads=[{"id":"P1","center":(1,2),"size_x":1.0,"size_y":2.0}]
    r=reconstruct_mask_openings(pads,expansion_mm=.05)
    assert r.openings[0].size==(1.1,2.1)
    assert validate_mask_openings(r.openings)==[]
