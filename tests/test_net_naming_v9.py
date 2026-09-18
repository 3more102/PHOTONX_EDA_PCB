from photonx_eda_pcb.net_naming.model import NetNameCandidate
from photonx_eda_pcb.net_naming import resolve_net_name,validate_resolved_name
def test_net_name_prefers_high_confidence():
    c=[NetNameCandidate("n1","VCC",.55,"heuristic"),NetNameCandidate("n1","+3V3",.98,"ipc356")]
    r=resolve_net_name("n1",c)
    assert r.name=="+3V3" and r.conflicts==("VCC",)
    assert validate_resolved_name(r)==[]
