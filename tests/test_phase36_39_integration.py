from photonx_eda_pcb.models import BoardModel,PadCandidate,DrillHit,OutlineSegment,Point
from photonx_eda_pcb.drc import run_drc
def loop(pts):return [OutlineSegment("E"+str(i),Point(*pts[i]),Point(*pts[(i+1)%len(pts)])) for i in range(len(pts))]
def test_precision_geometry_drc_pipeline():
    p=PadCandidate("P",Point(5,5),2,1,"O","F.Cu",drill=.4,net_id="N1")
    d=DrillHit("D",Point(5,5),.4,"plated")
    b=BoardModel(pads=[p],drills=[d],outline=loop([(0,0),(10,0),(10,10),(0,10)]))
    issues=run_drc(b)
    assert not any(x.code in {"ANNULAR_RING_BROKEN","COPPER_OUTSIDE_BOARD","DRILL_OUTSIDE_BOARD"} for x in issues)
