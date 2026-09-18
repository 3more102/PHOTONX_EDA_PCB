from .base import CheckIssue
from ..core.numeric import is_finite_number
def check_geometry(board):
    issues=[]
    for t in board.tracks:
        if not is_finite_number(t.width) or t.width<=0:issues.append(CheckIssue("error","TRACK_WIDTH_INVALID","track width must be positive",t.id))
    for p in board.pads:
        if p.size_x<=0 or p.size_y<=0:issues.append(CheckIssue("error","PAD_SIZE_INVALID","pad size must be positive",p.id))
    for d in board.drills:
        if d.diameter<=0:issues.append(CheckIssue("error","DRILL_DIAMETER_INVALID","drill diameter must be positive",d.id))
    for region in getattr(board,"regions",()):
        vals=[v for p in region.points for v in (p.x,p.y)]
        if not all(is_finite_number(v) for v in vals):issues.append(CheckIssue("error","REGION_COORDINATE_INVALID","region coordinates must be finite",region.id))
    for s in getattr(board,"slots",()):
        if not is_finite_number(s.width_mm) or s.width_mm<=0:issues.append(CheckIssue("error","SLOT_WIDTH_INVALID","slot width must be positive",s.id))
        vals=(*s.start,*s.end)
        if not all(is_finite_number(v) for v in vals):issues.append(CheckIssue("error","SLOT_COORDINATE_INVALID","slot coordinates must be finite",s.id))
    return issues
