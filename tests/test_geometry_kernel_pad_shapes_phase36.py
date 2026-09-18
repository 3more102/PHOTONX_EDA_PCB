import math
from photonx_eda_pcb.models import PadCandidate,Point
from photonx_eda_pcb.geometry_kernel import pad_shape
def test_circle_rectangle_and_oval_shapes():
    c=pad_shape(PadCandidate("c",Point(0,0),2,2,"C","F.Cu"))
    r=pad_shape(PadCandidate("r",Point(0,0),4,2,"R","F.Cu"))
    o=pad_shape(PadCandidate("o",Point(0,0),4,2,"O","F.Cu"))
    assert round(c.area,2)==round(math.pi,2)
    assert r.bounds==(-2.0,-1.0,2.0,1.0)
    assert o.bounds==(-2.0,-1.0,2.0,1.0)
    assert r.area>o.area>c.area
