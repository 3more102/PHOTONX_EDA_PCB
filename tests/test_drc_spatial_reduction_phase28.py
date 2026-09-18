from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.drc.model import DrcConfig
from photonx_eda_pcb.drc.spatial_metrics import clearance_candidate_metrics
def test_drc_candidate_reduction():
    pads=[]
    for i in range(100):pads.append(PadCandidate(str(i),Point(i*3,0),.5,.5,"C","F.Cu",net_id="N"+str(i)))
    m=clearance_candidate_metrics(BoardModel(pads=pads),DrcConfig(min_clearance_mm=.15))
    assert m["spatial_candidate_pairs"]<m["same_layer_bruteforce_pairs"]
    assert m["reduction_ratio"]>.8
