from math import hypot
from .model import AABB
from .grid import SpatialHashIndex
from .native_backend import (
    NativeBackendUnavailable,
    NativeBackendUnsupported,
    native_radius_queries,
)

def point_box(x,y,radius=0.0):
    r=max(0.0,float(radius));x=float(x);y=float(y)
    return AABB(x-r,y-r,x+r,y+r)

def build_point_index(items,xy_fn,cell_size=1.0):
    idx=SpatialHashIndex(cell_size)
    for obj_id,obj in items:
        x,y=xy_fn(obj);idx.insert(obj_id,point_box(x,y))
    return idx

def _radius_query_python(index,x,y,radius):
    q=point_box(x,y,radius);out=[]
    for oid in index.query(q):
        b=index.box(oid);cx=(b.min_x+b.max_x)/2;cy=(b.min_y+b.max_y)/2
        d=hypot(float(x)-cx,float(y)-cy)
        if d<=float(radius):out.append((d,oid))
    return sorted(out,key=lambda item:(item[0],item[1]))

def _radius_queries_python(index,queries):
    return [_radius_query_python(index,x,y,radius) for x,y,radius in queries]

def radius_queries(index,queries,backend="auto"):
    specs=tuple((float(x),float(y),float(radius)) for x,y,radius in queries)
    selected=str(backend).lower()
    if selected not in {"auto","python","native"}:
        raise ValueError("backend must be 'auto', 'python', or 'native'")
    if selected!="python":
        try:
            return native_radius_queries(index,specs)
        except (NativeBackendUnavailable,NativeBackendUnsupported):
            if selected=="native":
                raise
    return _radius_queries_python(index,specs)

def radius_query(index,x,y,radius,backend="auto"):
    return radius_queries(index,((x,y,radius),),backend=backend)[0]
