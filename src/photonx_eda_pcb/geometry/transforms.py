from math import cos,sin,radians
from ..models import Point
def translate(p:Point,dx:float,dy:float)->Point: return Point(p.x+dx,p.y+dy)
def scale(p:Point,sx:float,sy:float|None=None)->Point:
    sy=sx if sy is None else sy; return Point(p.x*sx,p.y*sy)
def rotate(p:Point,degrees:float,origin:Point=Point(0.0,0.0))->Point:
    a=radians(degrees); x=p.x-origin.x; y=p.y-origin.y
    return Point(origin.x+x*cos(a)-y*sin(a), origin.y+x*sin(a)+y*cos(a))
