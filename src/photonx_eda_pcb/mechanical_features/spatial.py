from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex
def _bounds(shape,expand=0.0):
    x0,y0,x1,y1=shape.bounds
    return AABB(x0-expand,y0-expand,x1+expand,y1+expand)
def nearby_object_ids(feature_shape,objects,shape_fn,minimum_mm,cell_size_mm=None):
    if not objects:return []
    idx=SpatialHashIndex(float(cell_size_mm or max(1.0,float(minimum_mm)*8)))
    shapes={}
    for o in objects:
        s=shape_fn(o);shapes[o.id]=s;idx.insert(o.id,_bounds(s))
    ids=idx.query(_bounds(feature_shape,float(minimum_mm)))
    return [(oid,shapes[oid]) for oid in ids]
