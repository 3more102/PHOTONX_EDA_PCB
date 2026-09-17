from dataclasses import dataclass
@dataclass
class RouteState:
    routing:bool=False
    x:float=0.0
    y:float=0.0
    tool:int|None=None
    def begin(self): self.routing=True
    def end(self): self.routing=False
