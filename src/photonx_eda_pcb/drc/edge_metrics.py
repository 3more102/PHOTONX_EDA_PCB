from .edge import outline_geometry
from photonx_eda_pcb.connectivity.geometry import copper_shape

def edge_clearance_metrics(board):
    boundary,outer=outline_geometry(board)
    if boundary is None:return {"objects":0,"minimum_clearance_mm":None,"outside_objects":0,"closed_outline":False}
    objs=[*board.tracks,*board.pads,*getattr(board,"regions",())]
    shapes=[copper_shape(o) for o in objs]
    dist=[shape.distance(boundary) for shape in shapes]
    outside=sum(1 for shape in shapes if outer is not None and not outer.covers(shape))
    return {"objects":len(objs),"minimum_clearance_mm":None if not dist else round(min(dist),6),"outside_objects":outside,"closed_outline":outer is not None}
