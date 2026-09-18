from shapely.geometry import Polygon
from shapely.ops import unary_union

def island_shape(island):
    pts=list(island.polygon)
    if len(pts)<3:return Polygon()
    return Polygon(pts)

def zone_shape(zone):
    shapes=[island_shape(i) for i in zone.islands]
    shapes=[s for s in shapes if not s.is_empty]
    return unary_union(shapes) if shapes else Polygon()
