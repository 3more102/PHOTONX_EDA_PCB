from dataclasses import dataclass,field
from photonx_eda_pcb.provenance import Provenance
@dataclass(frozen=True)
class RouteSegment:
    start:tuple[float,float]
    end:tuple[float,float]
@dataclass(frozen=True)
class RoutedPath:
    id:str
    points:tuple[tuple[float,float],...]
    width_mm:float
    plated:str="unknown"
    tool:str|None=None
    provenance:Provenance=field(default_factory=Provenance,compare=False)
    layer_span:tuple[str,str]|None=None
    span_proven:bool=False
    x2_layer_span:tuple[int,int]|None=None
    x2_span_kind:str|None=None
    x2_aperture_function:str|None=None
    @property
    def segments(self):
        return tuple(RouteSegment(self.points[i],self.points[i+1]) for i in range(max(0,len(self.points)-1)))
