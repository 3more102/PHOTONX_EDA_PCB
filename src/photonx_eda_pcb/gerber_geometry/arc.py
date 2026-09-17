from dataclasses import dataclass
from math import atan2,cos,sin,pi
from .model import GeoPoint
@dataclass(frozen=True)
class ArcSpec:
    start:GeoPoint; end:GeoPoint; center:GeoPoint; clockwise:bool=False
def sweep_radians(spec):
    a=atan2(spec.start.y-spec.center.y,spec.start.x-spec.center.x); b=atan2(spec.end.y-spec.center.y,spec.end.x-spec.center.x)
    d=b-a
    if spec.clockwise:
        if d>=0:d-=2*pi
    elif d<=0:d+=2*pi
    return d
def arc_points(spec,segments=32):
    if segments<1: raise ValueError('segments must be positive')
    a=atan2(spec.start.y-spec.center.y,spec.start.x-spec.center.x); d=sweep_radians(spec); r=((spec.start.x-spec.center.x)**2+(spec.start.y-spec.center.y)**2)**0.5
    return [GeoPoint(spec.center.x+r*cos(a+d*i/segments),spec.center.y+r*sin(a+d*i/segments)) for i in range(segments+1)]
