from photonx_eda_pcb.gerber_geometry.arc import ArcSpec,arc_points
from photonx_eda_pcb.gerber_geometry.model import GeoPoint
def test_arc():
    pts=arc_points(ArcSpec(GeoPoint(1,0),GeoPoint(0,1),GeoPoint(0,0)),segments=4); assert len(pts)==5; assert round(pts[-1].y,6)==1
