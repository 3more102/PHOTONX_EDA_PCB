from __future__ import annotations
from math import hypot
from ..models import BoardModel
from ..provenance import Evidence
from ..spatial_connectivity.points import build_point_index,radius_query

def _attach(pad,drill):
    pad.drill=drill.diameter
    pad.provenance.add_evidence(Evidence("drill_overlap",f"matched {drill.id} within tolerance",0.98,drill.provenance.sources[0] if drill.provenance.sources else None))

def attach_drills_bruteforce(board:BoardModel,tolerance_mm:float=0.15)->int:
    attached=0
    for pad in board.pads:
        candidates=[]
        for drill in board.drills:
            d=hypot(pad.center.x-drill.center.x,pad.center.y-drill.center.y)
            if d<=tolerance_mm:candidates.append((d,drill.id,drill))
        if not candidates:continue
        _,_,drill=min(candidates,key=lambda x:(x[0],x[1]));_attach(pad,drill);attached+=1
    return attached

def attach_drills(board:BoardModel,tolerance_mm:float=0.15,*,use_spatial_index:bool=True,cell_size_mm:float|None=None)->int:
    if not use_spatial_index:return attach_drills_bruteforce(board,tolerance_mm)
    if not board.drills or not board.pads:return 0
    idx=build_point_index(((d.id,d) for d in board.drills),lambda d:(d.center.x,d.center.y),float(cell_size_mm or max(1.0,tolerance_mm*8)))
    by_id={d.id:d for d in board.drills};attached=0
    for pad in board.pads:
        candidates=radius_query(idx,pad.center.x,pad.center.y,tolerance_mm)
        if not candidates:continue
        _,did=candidates[0];_attach(pad,by_id[did]);attached+=1
    return attached
