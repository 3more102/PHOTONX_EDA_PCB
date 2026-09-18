from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex,candidate_pairs,validate_index
def test_spatial_hash_candidate_pairs():
    i=SpatialHashIndex(1.0);i.insert("a",AABB(0,0,1,1));i.insert("b",AABB(.9,.9,2,2));i.insert("c",AABB(5,5,6,6))
    assert candidate_pairs(i)==[("a","b")]
    assert validate_index(i)==[]
