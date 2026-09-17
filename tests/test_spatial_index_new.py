from photonx_eda_pcb.spatial_index import BBox,GridIndex
def test_grid_index_query():
    index=GridIndex(1.0); index.insert("a",BBox(0,0,.5,.5)); index.insert("b",BBox(3,3,4,4))
    assert index.query(BBox(.25,.25,.3,.3))==["a"]
