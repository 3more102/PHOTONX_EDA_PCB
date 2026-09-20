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
        rings=(region.points,*getattr(region,"holes",()))
        vals=[v for ring in rings for p in ring for v in (p.x,p.y)]
        if not all(is_finite_number(v) for v in vals):issues.append(CheckIssue("error","REGION_COORDINATE_INVALID","region coordinates must be finite",region.id))
    for s in getattr(board,"slots",()):
        if not is_finite_number(s.width_mm) or s.width_mm<=0:issues.append(CheckIssue("error","SLOT_WIDTH_INVALID","slot width must be positive",s.id))
        vals=(*s.start,*s.end)
        if not all(is_finite_number(v) for v in vals):issues.append(CheckIssue("error","SLOT_COORDINATE_INVALID","slot coordinates must be finite",s.id))
    for route in getattr(board,"routes",()):
        if not is_finite_number(route.width_mm) or route.width_mm<=0:issues.append(CheckIssue("error","ROUTE_WIDTH_INVALID","route width must be finite and positive",route.id))
        if not all(
            isinstance(point,(tuple,list))
            and len(point)==2
            and all(is_finite_number(value) for value in point)
            for point in route.points
        ):issues.append(CheckIssue("error","ROUTE_COORDINATE_INVALID","route coordinates must be finite 2D points",route.id))
    return issues
