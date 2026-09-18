from .geometry import point_in_bounds
from .model import KeepoutViolation
def check_keepouts(objects,keepouts):
    out=[]
    for o in objects:
        oid=str(getattr(o,"id",getattr(o,"reference","")))
        p=getattr(o,"center",None)
        if p is None:continue
        point=(float(p[0]),float(p[1])) if isinstance(p,(tuple,list)) else (float(p.x),float(p.y))
        for k in keepouts:
            if point_in_bounds(point,k.bounds):out.append(KeepoutViolation(k.id,oid,k.kind))
    return out
