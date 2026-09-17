from .model import DrcIssue
def check_annular_ring(board,cfg):
    issues=[]
    for p in board.pads:
        if p.drill is None:continue
        ring=(min(p.size_x,p.size_y)-p.drill)/2
        if ring<cfg.min_annular_ring_mm:issues.append(DrcIssue('warning','ANNULAR_RING_MIN',f'annular ring {ring:.4f} mm',(p.id,)))
    return issues
