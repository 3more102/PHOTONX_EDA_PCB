from photonx_eda_pcb.differential_pairs import infer_pairs,pair_skew
def test_diff_pair_inference():
    p=infer_pairs(["USB_D_P","USB_D_N"],{"USB_D_P":10.0,"USB_D_N":10.2})
    assert len(p)==1 and p[0].confidence>=.65
    assert round(pair_skew([(0,0),(10,0)],[(0,0),(9,0)]),6)==1
