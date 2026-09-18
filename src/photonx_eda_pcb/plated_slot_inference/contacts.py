from photonx_eda_pcb.mechanical_features.geometry import slot_shape
from photonx_eda_pcb.geometry_kernel import pad_shape
from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex
def _box(shape,expand=0.0):
    x0,y0,x1,y1=shape.bounds;return AABB(x0-expand,y0-expand,x1+expand,y1+expand)
def slot_pad_contacts(board,slot,tolerance_mm=.03):
    if not board.pads:return []
    shapes={p.id:pad_shape(p) for p in board.pads};by={p.id:p for p in board.pads}
    idx=SpatialHashIndex(max(1.0,float(tolerance_mm)*8))
    for p in board.pads:idx.insert(p.id,_box(shapes[p.id]))
    ss=slot_shape(slot);out=[]
    for pid in idx.query(_box(ss,tolerance_mm)):
        ps=shapes[pid]
        if ps.buffer(tolerance_mm).intersects(ss):out.append(by[pid])
    return sorted(out,key=lambda p:(p.layer,p.id))
