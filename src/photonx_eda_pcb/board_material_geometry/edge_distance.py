def edge_distance(material,shape):
    if material is None:return None
    return float(shape.distance(material.boundary))
def minimum_edge_distance(material,shapes):
    vals=[edge_distance(material,s) for s in shapes]
    vals=[v for v in vals if v is not None]
    return None if not vals else min(vals)
