from photonx_eda_pcb.image_alignment import fit_affine
from photonx_eda_pcb.image_alignment.control_points import ControlPoint
from photonx_eda_pcb.image_alignment.metrics import rms_error
def test_affine_fit_exact_three_points():
    points=[ControlPoint(0,0,10,20),ControlPoint(1,0,12,20),ControlPoint(0,1,10,23)]
    transform=fit_affine(points)
    assert transform.apply(2,2)==(14.0,26.0)
    assert rms_error(transform,points)<1e-9
