from .model import AABB
def aabb_from_bounds(bounds):
    x0,y0,x1,y1=map(float,bounds);return AABB(min(x0,x1),min(y0,y1),max(x0,x1),max(y0,y1))
def build_index(items,bounds_fn,cell_size=1.0):
    from .grid import SpatialHashIndex
    idx=SpatialHashIndex(cell_size)
    for obj_id,item in items:idx.insert(obj_id,aabb_from_bounds(bounds_fn(item)))
    return idx
