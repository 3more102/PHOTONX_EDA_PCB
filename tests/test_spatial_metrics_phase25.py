from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex
from photonx_eda_pcb.spatial_connectivity.metrics import spatial_metrics
def test_spatial_metrics():
    i=SpatialHashIndex(2);i.insert("a",AABB(0,0,1,1));i.insert("b",AABB(3,0,4,1))
    m=spatial_metrics(i);assert m["objects"]==2 and m["cells"]>=2
