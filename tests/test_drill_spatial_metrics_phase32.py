from photonx_eda_pcb.models import BoardModel,PadCandidate,DrillHit,Point
from photonx_eda_pcb.connectivity.drill_metrics import drill_association_candidate_metrics
def test_drill_candidate_reduction():
    pads=[PadCandidate(f"P{i}",Point(i*5,0),1,1,"C","F.Cu") for i in range(100)]
    drills=[DrillHit(f"D{i}",Point(i*5,0),.4) for i in range(100)]
    m=drill_association_candidate_metrics(BoardModel(pads=pads,drills=drills),.1)
    assert m["spatial_candidates"]==100
    assert m["reduction_ratio"]>.95
