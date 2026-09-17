from photonx_eda_pcb.models import *
from photonx_eda_pcb.drc import run_drc

def test_cross_net_clearance():
 a=Track('a',Point(0,0),Point(2,0),.2,'F.Cu','N1'); b=Track('b',Point(0,.2),Point(2,.2),.2,'F.Cu','N2'); board=BoardModel(tracks=[a,b]); assert any(x.code=='COPPER_CLEARANCE' for x in run_drc(board))
