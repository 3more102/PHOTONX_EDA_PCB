from math import hypot
from ..models import Point
def segment_length(a:Point,b:Point)->float: return hypot(a.x-b.x,a.y-b.y)
def point_to_segment_distance(p:Point,a:Point,b:Point)->float:
    dx=b.x-a.x; dy=b.y-a.y
    if dx==0 and dy==0:return hypot(p.x-a.x,p.y-a.y)
    t=((p.x-a.x)*dx+(p.y-a.y)*dy)/(dx*dx+dy*dy); t=max(0.0,min(1.0,t))
    qx=a.x+t*dx; qy=a.y+t*dy
    return hypot(p.x-qx,p.y-qy)
