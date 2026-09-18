from photonx_eda_pcb.subgraph_fingerprints.geometry import relative_geometry_signature,geometry_similarity
def test_relative_geometry_ignores_translation():
    a=relative_geometry_signature(["A","B"],{"A":(0,0),"B":(2,0)})
    b=relative_geometry_signature(["C","D"],{"C":(10,10),"D":(12,10)})
    assert geometry_similarity(a,b)==1.0
