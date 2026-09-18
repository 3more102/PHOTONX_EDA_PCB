from shapely.ops import unary_union
from .convert import to_shape,from_shape
def union_polygons(polygons):
    return from_shape(unary_union([to_shape(p) for p in polygons]))
def intersect_polygons(a,b):
    return from_shape(to_shape(a).intersection(to_shape(b)))
def subtract_polygons(a,b):
    return from_shape(to_shape(a).difference(to_shape(b)))
