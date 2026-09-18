from math import hypot
from .model import AABB
from .grid import SpatialHashIndex

def point_box(x,y,radius=0.0):
    r=max(0.0,float(radius));x=float(x);y=float(y)
    return AABB(x-r,y-r,x+r,y+r)

def build_point_index(items,xy_fn,cell_size=1.0):
    idx=SpatialHashIndex(cell_size)
    for obj_id,obj in items:
        x,y=xy_fn(obj);idx.insert(obj_id,point_box(x,y))
    return idx

def radius_query(index,x,y,radius):
    q=point_box(x,y,radius);out=[]
    for oid in index.query(q):
        b=index.box(oid);cx=(b.min_x+b.max_x)/2;cy=(b.min_y+b.max_y)/2
        d=hypot(float(x)-cx,float(y)-cy)
        if d<=float(radius):out.append((d,oid))
    return sorted(out,key=lambda x:(x[0],x[1]))
