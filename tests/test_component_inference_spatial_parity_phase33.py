from copy import deepcopy
from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.inference.components import infer_component_hypotheses,infer_component_hypotheses_bruteforce
def make_board():
    return BoardModel(pads=[PadCandidate("A",Point(0,0),.5,.5,"C","F.Cu"),PadCandidate("B",Point(1,0),.5,.5,"C","F.Cu"),PadCandidate("C",Point(10,0),.5,.5,"C","F.Cu")])
def sig(items):return [(x.id,tuple(x.pad_ids),x.kind,x.confidence) for x in items]
def test_component_inference_spatial_parity():
    a=make_board();b=deepcopy(a)
    assert sig(infer_component_hypotheses_bruteforce(a,2))==sig(infer_component_hypotheses(b,2))
