from ..models import Point
def is_closed(points:list[Point], tol:float=1e-9)->bool:
    if len(points)<3:return False
    a,b=points[0],points[-1]; return abs(a.x-b.x)<=tol and abs(a.y-b.y)<=tol
def signed_area(points:list[Point])->float:
    if len(points)<3:return 0.0
    pts=points if is_closed(points) else [*points,points[0]]
    return 0.5*sum(a.x*b.y-b.x*a.y for a,b in zip(pts,pts[1:]))
