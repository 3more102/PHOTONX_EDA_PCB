from photonx_eda_pcb.paste_reconstruction import reconstruct_paste,validate_paste
def test_paste_skips_drilled():
    pads=[{"id":"S","center":(0,0),"size_x":1,"size_y":1,"drill":None},{"id":"T","center":(2,0),"size_x":1,"size_y":1,"drill":.4}]
    out=reconstruct_paste(pads,.1)
    assert [x.source_id for x in out]==["S"]
    assert out[0].size==(.9,.9)
    assert validate_paste(out)==[]
