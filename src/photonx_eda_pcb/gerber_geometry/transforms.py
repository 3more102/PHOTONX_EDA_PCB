from math import cos,sin,radians
from .model import GeoPoint
def translate(p,dx=0.0,dy=0.0): return GeoPoint(p.x+dx,p.y+dy)
def rotate(p,degrees,origin=GeoPoint(0,0)):
    a=radians(degrees); x=p.x-origin.x; y=p.y-origin.y
    return GeoPoint(origin.x+x*cos(a)-y*sin(a),origin.y+x*sin(a)+y*cos(a))
def mirror(p,x=False,y=False): return GeoPoint(-p.x if x else p.x,-p.y if y else p.y)
