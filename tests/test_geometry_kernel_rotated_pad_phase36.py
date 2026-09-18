from photonx_eda_pcb.models import PadCandidate,Point
from photonx_eda_pcb.geometry_kernel import pad_shape
def test_optional_rotation_attribute_is_honored():
    p=PadCandidate("r",Point(0,0),4,2,"R","F.Cu")
    p.rotation_deg=90
    s=pad_shape(p)
    x0,y0,x1,y1=s.bounds
    assert round(x1-x0,6)==2 and round(y1-y0,6)==4
