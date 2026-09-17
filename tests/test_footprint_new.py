from photonx_eda_pcb.models import *
from photonx_eda_pcb.footprints.matcher import match_signature
from photonx_eda_pcb.footprints.orientation import principal_orientation_deg

def test_two_pin_tht_match():
 pads=[PadCandidate('a',Point(0,0),1.5,1.5,'C','F.Cu',.8),PadCandidate('b',Point(5,0),1.5,1.5,'C','F.Cu',.8)]; m=match_signature(pads); assert m['best']=='TWO_PIN_THT'; assert m['confidence']>.5; assert abs(principal_orientation_deg(pads))<1e-6
