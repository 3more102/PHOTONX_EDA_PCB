from math import hypot
from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex

def _pad_box(p,tolerance_mm):
    r=max(float(tolerance_mm),max(float(p.size_x),float(p.size_y))/2)
    return AABB(p.center.x-r,p.center.y-r,p.center.x+r,p.center.y+r)

def build_pad_candidate_index(board,tolerance_mm=.15,cell_size_mm=None):
    idx=SpatialHashIndex(float(cell_size_mm or max(1.0,tolerance_mm*8)))
    for p in board.pads:idx.insert(p.id,_pad_box(p,tolerance_mm))
    return idx,{p.id:p for p in board.pads}

def pads_near_drill_bruteforce(board,drill,tolerance_mm=.15):
    out=[]
    for p in board.pads:
        r=max(p.size_x,p.size_y)/2
        if hypot(p.center.x-drill.center.x,p.center.y-drill.center.y)<=max(tolerance_mm,r):out.append(p)
    return sorted(out,key=lambda p:p.id)

def pads_near_drill(board,drill,tolerance_mm=.15,*,index=None,pad_by_id=None):
    if index is None:
        index,pad_by_id=build_pad_candidate_index(board,tolerance_mm)
    q=AABB(drill.center.x,drill.center.y,drill.center.x,drill.center.y)
    out=[]
    for pid in index.query(q):
        p=pad_by_id[pid];r=max(p.size_x,p.size_y)/2
        if hypot(p.center.x-drill.center.x,p.center.y-drill.center.y)<=max(tolerance_mm,r):out.append(p)
    return sorted(out,key=lambda p:p.id)
