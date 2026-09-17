from photonx_eda_pcb.models import *
from photonx_eda_pcb.checks import run_all_checks
def test_checks_detect_multiple_faults():
 b=BoardModel(tracks=[Track("X",Point(0,0),Point(1,0),0,"F.Cu")],pads=[PadCandidate("X",Point(0,0),1,1,"C","F.Cu")],drills=[DrillHit("D",Point(0,0),-1,plating="maybe")],nets=[NetGroup("N",["missing"],1.2)],components=[ComponentHypothesis("C",["bad"],"candidate",1.1,[])])
 codes={i.code for i in run_all_checks(b)}
 assert {"DUPLICATE_OBJECT_ID","TRACK_WIDTH_INVALID","DRILL_DIAMETER_INVALID","NET_MEMBER_MISSING","NET_CONFIDENCE_INVALID","COMPONENT_PAD_MISSING","COMPONENT_CONFIDENCE_INVALID"}<=codes
