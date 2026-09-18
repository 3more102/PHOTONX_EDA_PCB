from shapely.geometry import Polygon
def to_shape(points):
    pts=[(float(x),float(y)) for x,y in points]
    if len(pts)<3: raise ValueError("polygon requires at least three points")
    p=Polygon(pts)
    if not p.is_valid: p=p.buffer(0)
    return p
def from_shape(shape):
    if shape.is_empty:return []
    geoms=list(shape.geoms) if hasattr(shape,"geoms") else [shape]
    out=[]
    for g in geoms:
        if g.geom_type=="Polygon":
            out.append(tuple((round(x,12),round(y,12)) for x,y in list(g.exterior.coords)[:-1]))
    return out
