from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex,candidate_pairs

def _bounds(shape):
    x0,y0,x1,y1=shape.bounds
    return AABB(float(x0),float(y0),float(x1),float(y1))

def layer_candidate_pairs(objects,shapes,tolerance_mm=0.03,cell_size_mm=None):
    by_layer={}
    for obj in objects:by_layer.setdefault(obj.layer,[]).append(obj)
    out=[]
    for layer,items in sorted(by_layer.items(),key=lambda kv:str(kv[0])):
        if len(items)<2:continue
        cell=float(cell_size_mm or max(1.0,float(tolerance_mm)*8.0))
        idx=SpatialHashIndex(cell)
        for obj in items:idx.insert(obj.id,_bounds(shapes[obj.id]))
        out.extend(candidate_pairs(idx,float(tolerance_mm)))
    return sorted(set(out))
