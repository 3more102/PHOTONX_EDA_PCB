from .model import DrcIssue
from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex,candidate_pairs
from photonx_eda_pcb.geometry_kernel import object_shape

def _shape(o):return object_shape(o)

def _bounds(s):
    x0,y0,x1,y1=s.bounds;return AABB(float(x0),float(y0),float(x1),float(y1))

def _issue(a,b,cfg):
    return DrcIssue("error","COPPER_CLEARANCE",f"clearance below {cfg.min_clearance_mm} mm",(a.id,b.id))

def check_clearance_bruteforce(board,cfg):
    objs=[*board.tracks,*board.pads,*getattr(board,"regions",())];out=[];shapes={o.id:_shape(o) for o in objs}
    for i,a in enumerate(objs):
        for b in objs[i+1:]:
            if getattr(a,"layer",None)!=getattr(b,"layer",None):continue
            if a.net_id is None or b.net_id is None or a.net_id==b.net_id:continue
            if shapes[a.id].distance(shapes[b.id])<cfg.min_clearance_mm:out.append(_issue(a,b,cfg))
    return out

def check_clearance(board,cfg,*,use_spatial_index=True,cell_size_mm=None):
    if not use_spatial_index:return check_clearance_bruteforce(board,cfg)
    objs=[*board.tracks,*board.pads,*getattr(board,"regions",())];out=[];shapes={o.id:_shape(o) for o in objs};by_layer={}
    for o in objs:by_layer.setdefault(getattr(o,"layer",None),[]).append(o)
    index={o.id:o for o in objs}
    for layer,items in sorted(by_layer.items(),key=lambda kv:str(kv[0])):
        if len(items)<2:continue
        idx=SpatialHashIndex(float(cell_size_mm or max(1.0,cfg.min_clearance_mm*8)))
        for o in items:idx.insert(o.id,_bounds(shapes[o.id]))
        for aid,bid in candidate_pairs(idx,cfg.min_clearance_mm):
            a=index[aid];b=index[bid]
            if a.net_id is None or b.net_id is None or a.net_id==b.net_id:continue
            if shapes[aid].distance(shapes[bid])<cfg.min_clearance_mm:out.append(_issue(a,b,cfg))
    return sorted(out,key=lambda x:x.object_ids)
