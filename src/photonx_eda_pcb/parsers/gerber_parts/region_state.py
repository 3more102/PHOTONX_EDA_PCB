from dataclasses import dataclass,field
@dataclass
class RegionState:
    active:bool=False
    vertices:list[tuple[float,float]]=field(default_factory=list)
    def begin(self): self.active=True; self.vertices.clear()
    def add(self,x:float,y:float):
        if not self.active: raise RuntimeError("region not active")
        self.vertices.append((x,y))
    def end(self): self.active=False; return tuple(self.vertices)
