from photonx_eda_pcb.models import *
from photonx_eda_pcb.stackup import infer_stackup,validate_stackup

def test_stackup_two_layers():
 b=BoardModel(tracks=[Track('t',Point(0,0),Point(1,0),.2,'F.Cu'),Track('b',Point(0,1),Point(1,1),.2,'B.Cu')]); s=infer_stackup(b); assert [x.name for x in s.copper_layers()]==['F.Cu','B.Cu']; assert not [x for x in validate_stackup(s) if x.severity=='error']
