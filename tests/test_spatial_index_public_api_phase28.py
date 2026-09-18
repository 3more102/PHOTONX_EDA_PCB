from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex
def test_spatial_ids_and_boxes_are_deterministic():
    i=SpatialHashIndex();i.insert("b",AABB(2,0,3,1));i.insert("a",AABB(0,0,1,1))
    assert i.ids()==("a","b")
    assert list(i.boxes())==["a","b"]
