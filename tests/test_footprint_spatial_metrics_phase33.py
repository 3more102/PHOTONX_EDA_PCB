from photonx_eda_pcb.models import PadCandidate,Point
from photonx_eda_pcb.footprints.spatial_metrics import clustering_candidate_metrics
def test_footprint_candidate_reduction():
    pads=[PadCandidate(str(i),Point(i*10,0),.5,.5,"C","F.Cu") for i in range(100)]
    m=clustering_candidate_metrics(pads,2)
    assert m["spatial_neighbor_pairs"]==0 and m["reduction_ratio"]==1.0
