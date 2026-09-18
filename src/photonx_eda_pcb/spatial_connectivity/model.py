from dataclasses import dataclass
@dataclass(frozen=True)
class AABB:
    min_x:float
    min_y:float
    max_x:float
    max_y:float
    def expanded(self,d):
        v=float(d);return AABB(self.min_x-v,self.min_y-v,self.max_x+v,self.max_y+v)
    def intersects(self,other):
        return not (self.max_x<other.min_x or other.max_x<self.min_x or self.max_y<other.min_y or other.max_y<self.min_y)
