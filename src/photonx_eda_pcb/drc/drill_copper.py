from .model import DrcIssue
from photonx_eda_pcb.geometry_kernel import drill_shape,object_shape
from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex

def _box(shape,expand=0.0):
    x0,y0,x1,y1=shape.bounds
    return AABB(x0-expand,y0-expand,x1+expand,y1+expand)

def _associated_pad(drill,pad,tol=1e-9):
    if pad.drill is None:return False
    same_center=abs(pad.center.x-drill.center.x)<=tol and abs(pad.center.y-drill.center.y)<=tol
    same_diameter=abs(float(pad.drill)-float(drill.diameter))<=tol
    return same_center and same_diameter

def check_drill_copper_clearance(board,cfg):
    minimum=float(getattr(cfg,"min_drill_copper_clearance_mm",0.0))
    if minimum<=0 or not board.drills:return []
    copper=[*board.tracks,*board.pads,*getattr(board,"regions",())]
    if not copper:return []
    shapes={o.id:object_shape(o) for o in copper};objects={o.id:o for o in copper}
    idx=SpatialHashIndex(max(1.0,minimum*8))
    for o in copper:idx.insert(o.id,_box(shapes[o.id]))
    out=[]
    for d in board.drills:
        ds=drill_shape(d)
        for oid in idx.query(_box(ds,minimum)):
            o=objects[oid]
            if hasattr(o,"drill") and _associated_pad(d,o):continue
            dist=ds.distance(shapes[oid])
            if dist<minimum:
                sev="error" if getattr(d,"plating","unknown")=="non-plated" else "warning"
                out.append(DrcIssue(sev,"DRILL_COPPER_CLEARANCE",f"drill-to-copper clearance {dist:.6f} mm below {minimum} mm",(d.id,o.id)))
    return sorted(out,key=lambda x:x.object_ids)
