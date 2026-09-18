def classify_shape(material,shape):
    if material is None:return "unknown"
    if material.covers(shape):return "material"
    if material.intersects(shape):return "crosses_boundary"
    return "outside_or_cutout"
