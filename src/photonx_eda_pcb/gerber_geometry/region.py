from dataclasses import dataclass,field
from .model import GeoPoint,PolygonPrimitive
@dataclass
class RegionBuilder:
    points:list[GeoPoint]=field(default_factory=list)
    closed:bool=False
    def move(self,p): self.points=[p]; self.closed=False
    def line(self,p):
        if not self.points: raise ValueError('region has no start point')
        self.points.append(p)
    def close(self):
        if len(self.points)<3: raise ValueError('region needs at least three points')
        if self.points[-1]!=self.points[0]: self.points.append(self.points[0])
        self.closed=True; return PolygonPrimitive(tuple(self.points))
