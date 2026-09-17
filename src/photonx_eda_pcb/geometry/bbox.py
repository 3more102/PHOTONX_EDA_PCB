from dataclasses import dataclass
from ..models import Point, BoardModel
@dataclass(frozen=True)
class Bounds:
    min_x:float; min_y:float; max_x:float; max_y:float
    @property
    def width(self): return self.max_x-self.min_x
    @property
    def height(self): return self.max_y-self.min_y
def bounds_from_points(points:list[Point])->Bounds|None:
    if not points:return None
    xs=[p.x for p in points]; ys=[p.y for p in points]
    return Bounds(min(xs),min(ys),max(xs),max(ys))
def board_bounds(board:BoardModel)->Bounds|None:
    pts=[]
    for t in board.tracks: pts.extend([t.start,t.end])
    for p in board.pads: pts.append(p.center)
    for d in board.drills: pts.append(d.center)
    for s in board.outline: pts.extend([s.start,s.end])
    return bounds_from_points(pts)
