from photonx_eda_pcb.models import BoardModel,PadCandidate,DrillHit,Point
from photonx_eda_pcb.via_span.spatial_metrics import via_span_candidate_metrics
def test_via_span_candidate_reduction():
    pads=[PadCandidate(f"P{i}",Point(i*4,0),1,1,"C","F.Cu") for i in range(60)]
    drills=[DrillHit(f"D{i}",Point(i*4,0),.4) for i in range(60)]
    m=via_span_candidate_metrics(BoardModel(pads=pads,drills=drills),.15)
    assert m["spatial_candidates"]==60 and m["reduction_ratio"]>.95
