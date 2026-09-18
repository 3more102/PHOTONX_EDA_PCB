from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.mechanical_features.geometry import slot_shape
from photonx_eda_pcb.mechanical_features.metrics import clearance_candidate_metrics
from photonx_eda_pcb.models import PadCandidate,Point
from photonx_eda_pcb.geometry_kernel import object_shape
def test_mechanical_spatial_candidate_reduction():
    features=[slot_shape(SlotFeature("S",(0,0),(2,0),.5))]
    objs=[PadCandidate(str(i),Point(i*5,10),.5,.5,"C","F.Cu") for i in range(100)]
    m=clearance_candidate_metrics(features,objs,object_shape,.2)
    assert m["spatial_candidates"]<m["bruteforce_pairs"] and m["reduction_ratio"]>.9
