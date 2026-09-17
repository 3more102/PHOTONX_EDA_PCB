from photonx_eda_pcb.gerber_geometry.aperture_geometry import aperture_bbox
def test_bbox(): assert aperture_bbox('R',2,4)==(-1,-2,1,2)
