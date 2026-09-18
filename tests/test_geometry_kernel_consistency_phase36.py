from photonx_eda_pcb.models import PadCandidate,Point
from photonx_eda_pcb.geometry_kernel import pad_shape
from photonx_eda_pcb.connectivity.geometry import copper_shape
from photonx_eda_pcb.drc.clearance import _shape
def test_connectivity_and_drc_share_geometry_kernel():
    p=PadCandidate("o",Point(1,2),4,2,"O","F.Cu")
    assert copper_shape(p).equals(pad_shape(p))
    assert _shape(p).equals(pad_shape(p))
