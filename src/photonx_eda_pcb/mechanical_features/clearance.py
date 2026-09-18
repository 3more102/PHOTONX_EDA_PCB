def clearance_to_objects(feature_shape,objects,shape_fn,minimum_mm,*,use_spatial_index=True):
    out=[]
    if use_spatial_index:
        from .spatial import nearby_object_ids
        candidates=nearby_object_ids(feature_shape,list(objects),shape_fn,minimum_mm)
        for oid,shape in candidates:
            d=feature_shape.distance(shape)
            if d<float(minimum_mm):out.append((oid,round(float(d),6)))
        return sorted(out)
    for obj in objects:
        d=feature_shape.distance(shape_fn(obj))
        if d<float(minimum_mm):out.append((obj.id,round(float(d),6)))
    return sorted(out)
