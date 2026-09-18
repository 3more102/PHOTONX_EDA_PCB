from photonx_eda_pcb.via_transition import analyze_transition,validate_transition
from photonx_eda_pcb.via_transition.quality import transition_quality
def test_via_transition_quality():
    v=analyze_transition("V1","N1","F.Cu","B.Cu",.3,.7,2,0)
    assert validate_transition(v)==[]
    assert transition_quality(v,2)>.8
