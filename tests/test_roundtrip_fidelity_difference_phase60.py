from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.roundtrip_fidelity import evaluate_fidelity
def test_pad_difference_reduces_score():
    a=BoardModel(pads=[PadCandidate("P",Point(0,0),1,1,"C","F.Cu")])
    b=BoardModel()
    r=evaluate_fidelity(a,b)
    assert not r.exact and r.score<1.0
    assert any(x.name=="pads" and not x.equal for x in r.sections)
