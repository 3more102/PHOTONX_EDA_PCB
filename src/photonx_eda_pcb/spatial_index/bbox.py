from dataclasses import dataclass
@dataclass(frozen=True)
class BBox:
    min_x:float; min_y:float; max_x:float; max_y:float
    def intersects(self,other): return not (self.max_x<other.min_x or other.max_x<self.min_x or self.max_y<other.min_y or other.max_y<self.min_y)
    def expanded(self,distance): return BBox(self.min_x-distance,self.min_y-distance,self.max_x+distance,self.max_y+distance)
