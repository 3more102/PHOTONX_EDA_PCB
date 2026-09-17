from photonx_eda_pcb.models import *
from photonx_eda_pcb.drc import run_drc

def test_drc_width_and_drill():
 b=BoardModel(tracks=[Track('t',Point(0,0),Point(1,0),.05,'F.Cu')],drills=[DrillHit('d',Point(0,0),.1)]); codes={x.code for x in run_drc(b)}; assert 'TRACK_WIDTH_MIN' in codes and 'DRILL_MIN' in codes
