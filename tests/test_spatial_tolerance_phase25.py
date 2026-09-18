from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex,candidate_pairs
def test_spatial_tolerance_expands_query():
    i=SpatialHashIndex(1);i.insert("a",AABB(0,0,.2,.2));i.insert("b",AABB(.25,0,.4,.2))
    assert candidate_pairs(i)==[]
    assert candidate_pairs(i,.1)==[("a","b")]
