from photonx_eda_pcb.centroid_export.model import CentroidRecord
from photonx_eda_pcb.centroid_export.mirror import mirror_bottom_x
def test_bottom_mirror():
    r=mirror_bottom_x([CentroidRecord("U1",2,1,90,"bottom")],0)
    assert r[0].x_mm==-2 and r[0].rotation_deg==270
