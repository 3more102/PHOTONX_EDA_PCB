from .clearance import _shape
from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex,candidate_pairs

def clearance_candidate_metrics(board,cfg,cell_size_mm=None):
    objs=[*board.tracks,*board.pads];shapes={o.id:_shape(o) for o in objs};by={}
    for o in objs:by.setdefault(getattr(o,"layer",None),[]).append(o)
    total=0;candidates=0
    for items in by.values():
        total+=len(items)*(len(items)-1)//2
        if len(items)<2:continue
        idx=SpatialHashIndex(float(cell_size_mm or max(1.0,cfg.min_clearance_mm*8)))
        for o in items:
            x0,y0,x1,y1=shapes[o.id].bounds;idx.insert(o.id,AABB(x0,y0,x1,y1))
        candidates+=len(candidate_pairs(idx,cfg.min_clearance_mm))
    return {"same_layer_bruteforce_pairs":total,"spatial_candidate_pairs":candidates,"reduction_ratio":1.0 if total==0 else round(1-candidates/total,6)}
