from .model import DrcIssue
from photonx_eda_pcb.connectivity.geometry import copper_shape
from photonx_eda_pcb.geometry_kernel import drill_shape,object_shape
from photonx_eda_pcb.board_material_geometry import board_material_shape

def outline_geometry(board):
    material=board_material_shape(board)
    return (None,None) if material is None else (material.boundary,material)

def _edge_issue(kind,obj_id,distance,minimum):
    return DrcIssue("error",kind,f"edge clearance {distance:.6f} mm below {minimum} mm",(obj_id,))

def check_edge_presence(board,cfg):
    if not board.outline:return [DrcIssue("warning","BOARD_OUTLINE_MISSING","edge clearance cannot be evaluated without outline")]
    boundary,material=outline_geometry(board)
    if material is None:return [DrcIssue("warning","BOARD_OUTLINE_NOT_CLOSED","edge clearance uses outline segments but outside-board detection is unavailable")]
    out=[]
    for obj in [*board.tracks,*board.pads,*getattr(board,"regions",())]:
        shape=copper_shape(obj);distance=shape.distance(boundary)
        if not material.covers(shape):
            out.append(DrcIssue("error","COPPER_OUTSIDE_BOARD","copper extends outside board material or into a cutout",(obj.id,)))
        elif distance<cfg.edge_clearance_mm:
            out.append(_edge_issue("COPPER_EDGE_CLEARANCE",obj.id,distance,cfg.edge_clearance_mm))
    for drill in board.drills:
        shape=drill_shape(drill);distance=shape.distance(boundary)
        if not material.covers(shape):
            out.append(DrcIssue("error","DRILL_OUTSIDE_BOARD","drill extends outside board material or into a cutout",(drill.id,)))
        elif distance<cfg.edge_clearance_mm:
            out.append(_edge_issue("DRILL_EDGE_CLEARANCE",drill.id,distance,cfg.edge_clearance_mm))
    for slot in getattr(board,"slots",()):
        shape=object_shape(slot);distance=shape.distance(boundary)
        if not material.covers(shape):
            out.append(DrcIssue("error","SLOT_OUTSIDE_BOARD","slot extends outside board material or into a cutout",(slot.id,)))
        elif distance<cfg.edge_clearance_mm:
            out.append(_edge_issue("SLOT_EDGE_CLEARANCE",slot.id,distance,cfg.edge_clearance_mm))
    return sorted(out,key=lambda x:(x.code,x.object_ids))
