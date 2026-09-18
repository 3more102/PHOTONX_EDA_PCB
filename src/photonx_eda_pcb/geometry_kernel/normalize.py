from shapely.geometry import Polygon,MultiPolygon
def normalized_polygon(shape):
    if shape is None:return None
    if shape.is_valid:return shape
    fixed=shape.buffer(0)
    return fixed
def polygon_count(shape):
    if shape is None or shape.is_empty:return 0
    if isinstance(shape,Polygon):return 1
    if isinstance(shape,MultiPolygon):return len(shape.geoms)
    return 0
