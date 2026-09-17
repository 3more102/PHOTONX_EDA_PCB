from photonx_eda_pcb.gerber_geometry.region import RegionBuilder
from photonx_eda_pcb.gerber_geometry.model import GeoPoint
def test_region():
    r=RegionBuilder(); r.move(GeoPoint(0,0)); r.line(GeoPoint(1,0)); r.line(GeoPoint(1,1)); p=r.close(); assert p.points[0]==p.points[-1]
