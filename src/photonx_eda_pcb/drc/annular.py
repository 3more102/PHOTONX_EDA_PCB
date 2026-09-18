from shapely.geometry import Point as SPoint
from .model import DrcIssue
from photonx_eda_pcb.geometry_kernel import pad_shape

def annular_ring_mm(pad):
    if pad.drill is None:return None
    copper=pad_shape(pad)
    drill=SPoint(pad.center.x,pad.center.y).buffer(float(pad.drill)/2)
    if not copper.covers(drill):return -1.0
    return float(copper.boundary.distance(drill.boundary))

def check_annular_ring(board,cfg):
    issues=[]
    for p in board.pads:
        ring=annular_ring_mm(p)
        if ring is None:continue
        if ring<0:
            issues.append(DrcIssue("error","ANNULAR_RING_BROKEN","drill exceeds reconstructed pad copper",(p.id,)))
        elif ring<cfg.min_annular_ring_mm:
            issues.append(DrcIssue("warning","ANNULAR_RING_MIN",f"annular ring {ring:.4f} mm",(p.id,)))
    return issues
