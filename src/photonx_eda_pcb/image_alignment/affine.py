from dataclasses import dataclass
@dataclass(frozen=True)
class Affine2D:
    a:float=1.0; b:float=0.0; c:float=0.0; d:float=0.0; e:float=1.0; f:float=0.0
    def apply(self,x,y): return (self.a*x+self.b*y+self.c,self.d*x+self.e*y+self.f)
