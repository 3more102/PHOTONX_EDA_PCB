from photonx_eda_pcb.models import *
from photonx_eda_pcb.stackup import infer_stackup
from photonx_eda_pcb.via_span import resolve_via_spans

def test_via_span_proven_plated():
 p1=PadCandidate('p1',Point(0,0),1,1,'C','F.Cu',.4); p2=PadCandidate('p2',Point(0,0),1,1,'C','B.Cu',.4); d=DrillHit('d',Point(0,0),.4,'plated'); b=BoardModel(pads=[p1,p2],drills=[d]); s=infer_stackup(b); x=resolve_via_spans(b,s)[0]; assert x.proven and x.from_layer=='F.Cu' and x.to_layer=='B.Cu'
