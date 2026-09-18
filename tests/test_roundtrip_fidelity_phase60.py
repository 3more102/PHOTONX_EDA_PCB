from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.roundtrip_fidelity import evaluate_fidelity,validate_fidelity
def test_exact_roundtrip_scores_one():
    a=BoardModel(pads=[PadCandidate("P",Point(0,0),1,1,"C","F.Cu")])
    b=BoardModel(pads=[PadCandidate("P",Point(0,0),1,1,"C","F.Cu")])
    r=evaluate_fidelity(a,b)
    assert r.exact and r.score==1.0 and validate_fidelity(r)==[]
