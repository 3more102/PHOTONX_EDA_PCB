from photonx_eda_pcb.models import *
from photonx_eda_pcb.roundtrip import board_fingerprint,compare_board_models

def test_roundtrip_deterministic():
 a=BoardModel(tracks=[Track('t',Point(0,0),Point(1,0),.2,'F.Cu')]); b=BoardModel(tracks=[Track('t',Point(0,0),Point(1,0),.2,'F.Cu')]); assert board_fingerprint(a)==board_fingerprint(b); assert compare_board_models(a,b)==[]
