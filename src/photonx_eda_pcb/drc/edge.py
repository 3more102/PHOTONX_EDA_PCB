from shapely.geometry import LineString
from shapely.ops import unary_union,polygonize
from .model import DrcIssue
from photonx_eda_pcb.connectivity.geometry import copper_shape

def outline_geometry(board):
    lines=[LineString([(s.start.x,s.start.y),(s.end.x,s.end.y)]) for s in board.outline]
    if not lines:return None,None
    boundary=unary_union(lines)
    polygons=list(polygonize(boundary))
    outer=max(polygons,key=lambda p:p.area) if polygons else None
    return boundary,outer

def check_edge_presence(board,cfg):
    if not board.outline:return [DrcIssue("warning","BOARD_OUTLINE_MISSING","edge clearance cannot be evaluated without outline")]
    boundary,outer=outline_geometry(board)
    if outer is None:return [DrcIssue("warning","BOARD_OUTLINE_NOT_CLOSED","edge clearance uses outline segments but outside-board detection is unavailable")]
    out=[]
    for obj in [*board.tracks,*board.pads]:
        shape=copper_shape(obj)
        distance=shape.distance(boundary)
        if not outer.covers(shape):
            out.append(DrcIssue("error","COPPER_OUTSIDE_BOARD","copper extends outside reconstructed outer board outline",(obj.id,)))
        elif distance<cfg.edge_clearance_mm:
            out.append(DrcIssue("error","COPPER_EDGE_CLEARANCE",f"copper-to-edge clearance below {cfg.edge_clearance_mm} mm",(obj.id,)))
    return sorted(out,key=lambda x:(x.code,x.object_ids))
