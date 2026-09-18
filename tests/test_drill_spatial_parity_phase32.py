from copy import deepcopy
from photonx_eda_pcb.models import BoardModel,PadCandidate,DrillHit,Point
from photonx_eda_pcb.connectivity.drills import attach_drills,attach_drills_bruteforce
def make_board():
    return BoardModel(
        pads=[PadCandidate("P1",Point(0,0),1,1,"C","F.Cu"),PadCandidate("P2",Point(5,0),1,1,"C","F.Cu")],
        drills=[DrillHit("D1",Point(.03,0),.4),DrillHit("D2",Point(5.02,0),.6)]
    )
def test_drill_spatial_matches_bruteforce():
    a=make_board();b=deepcopy(a)
    assert attach_drills_bruteforce(a,.1)==attach_drills(b,.1)==2
    assert [(p.id,p.drill) for p in a.pads]==[(p.id,p.drill) for p in b.pads]
