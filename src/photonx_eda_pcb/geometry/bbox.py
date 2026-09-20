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

def _half_extent(value:float)->float:
    value=float(value)
    return value/2.0 if value>0 else 0.0

def _add_box(points:list[Point],min_x:float,min_y:float,max_x:float,max_y:float)->None:
    points.extend((Point(min_x,min_y),Point(max_x,max_y)))

def _add_segment_extent(points:list[Point],start_x:float,start_y:float,end_x:float,end_y:float,width:float)->None:
    radius=_half_extent(width)
    _add_box(
        points,
        min(float(start_x),float(end_x))-radius,
        min(float(start_y),float(end_y))-radius,
        max(float(start_x),float(end_x))+radius,
        max(float(start_y),float(end_y))+radius,
    )

def board_bounds(board:BoardModel)->Bounds|None:
    """Return the physical axis-aligned extent of reconstructed board geometry.

    Width/diameter-bearing features contribute their complete physical envelope
    rather than only centerlines or centers. Copper regions, slots and routed
    paths are included so bounds cover the complete BoardModel geometry.
    """
    pts:list[Point]=[]

    for t in board.tracks:
        _add_segment_extent(pts,t.start.x,t.start.y,t.end.x,t.end.y,t.width)

    for p in board.pads:
        hx=_half_extent(p.size_x); hy=_half_extent(p.size_y)
        _add_box(pts,p.center.x-hx,p.center.y-hy,p.center.x+hx,p.center.y+hy)

    for d in board.drills:
        radius=_half_extent(d.diameter)
        _add_box(pts,d.center.x-radius,d.center.y-radius,d.center.x+radius,d.center.y+radius)

    for s in board.outline:
        pts.extend((s.start,s.end))

    for slot in getattr(board,"slots",()):
        _add_segment_extent(
            pts,
            slot.start[0],slot.start[1],
            slot.end[0],slot.end[1],
            slot.width_mm,
        )

    for route in getattr(board,"routes",()):
        radius=_half_extent(route.width_mm)
        for x,y in route.points:
            _add_box(pts,float(x)-radius,float(y)-radius,float(x)+radius,float(y)+radius)

    for region in getattr(board,"regions",()):
        pts.extend(region.points)

    return bounds_from_points(pts)
