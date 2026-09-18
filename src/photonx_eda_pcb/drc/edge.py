from .model import DrcIssue
from photonx_eda_pcb.connectivity.geometry import copper_shape
from photonx_eda_pcb.geometry_kernel import drill_shape
from photonx_eda_pcb.board_material_geometry import board_material_shape

def outline_geometry(board):
    shape=board_material_shape(board)
    return (None,shape)

def check_edge_presence(board,cfg):
    if not board.outline:return [DrcIssue("warning","BOARD_OUTLINE_MISSING","edge clearance cannot be evaluated without outline")]
    material=board_material_shape(board)
    if material is None:return [DrcIssue("warning","BOARD_OUTLINE_NOT_CLOSED","edge clearance uses outline segments but outside-board detection is unavailable")]
    out=[];boundary=material.boundary
    for obj in [*board.tracks,*board.pads]:
        shape=copper_shape(obj);distance=shape.distance(boundary)
        if not material.covers(shape):
            out.append(DrcIssue("error","COPPER_OUTSIDE_BOARD","copper extends outside board material or into a cutout",(obj.id,)))
        elif distance<cfg.edge_clearance_mm:
            out.append(DrcIssue("error","COPPER_EDGE_CLEARANCE",f"copper-to-edge clearance below {cfg.edge_clearance_mm} mm",(obj.id,)))
    for drill in board.drills:
        shape=drill_shape(drill);distance=shape.distance(boundary)
        if not material.covers(shape):
            out.append(DrcIssue("error","DRILL_OUTSIDE_BOARD","drill extends outside board material or into a cutout",(drill.id,)))
        elif distance<cfg.edge_clearance_mm:
            out.append(DrcIssue("error","DRILL_EDGE_CLEARANCE",f"drill-to-edge clearance below {cfg.edge_clearance_mm} mm",(drill.id,)))
    return sorted(out,key=lambda x:(x.code,x.object_ids))
