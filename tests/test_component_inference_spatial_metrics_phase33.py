from photonx_eda_pcb.models import PadCandidate,Point
from photonx_eda_pcb.inference.component_spatial_metrics import component_pair_candidate_metrics
def test_component_pair_reduction():
    pads=[PadCandidate(str(i),Point(i*8,0),.5,.5,"C","F.Cu") for i in range(80)]
    m=component_pair_candidate_metrics(pads,2)
    assert m["spatial_neighbor_pairs"]==0 and m["reduction_ratio"]==1.0
