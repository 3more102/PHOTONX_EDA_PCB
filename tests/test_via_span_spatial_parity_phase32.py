from photonx_eda_pcb.models import BoardModel,PadCandidate,DrillHit,Point
from photonx_eda_pcb.stackup.model import StackupModel,LayerSpec
from photonx_eda_pcb.via_span.resolve import resolve_via_spans
def make_data():
    board=BoardModel(
      pads=[PadCandidate("F",Point(0,0),1,1,"C","F.Cu"),PadCandidate("B",Point(0,0),1,1,"C","B.Cu")],
      drills=[DrillHit("D",Point(0,0),.4,"plated")]
    )
    stack=StackupModel([LayerSpec("F.Cu","top",0,True),LayerSpec("B.Cu","bottom",1,True)])
    return board,stack
def test_via_span_spatial_matches_bruteforce():
    b,s=make_data()
    a=resolve_via_spans(b,s,use_spatial_index=False)[0]
    x=resolve_via_spans(b,s,use_spatial_index=True)[0]
    assert (a.from_layer,a.to_layer,a.confidence,a.proven)==(x.from_layer,x.to_layer,x.confidence,x.proven)
    assert x.proven and x.from_layer=="F.Cu" and x.to_layer=="B.Cu"
