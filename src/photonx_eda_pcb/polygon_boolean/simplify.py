from shapely.geometry import Polygon
from .convert import from_shape
def simplify_polygon(points,tolerance=1e-6):
    return from_shape(Polygon(points).simplify(float(tolerance),preserve_topology=True))
