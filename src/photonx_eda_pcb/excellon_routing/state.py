from dataclasses import dataclass,field
@dataclass
class LinearRouteState:
    positioned:bool=False
    tool_down:bool=False
    points:list[tuple[float,float]]=field(default_factory=list)
    def position(self,x,y):
        if self.tool_down:raise RuntimeError("cannot rapid-position while route tool is down")
        self.positioned=True;self.points=[(float(x),float(y))]
    def lower(self):
        if not self.positioned:raise RuntimeError("route start not positioned")
        if self.tool_down:raise RuntimeError("route tool already down")
        self.tool_down=True
    def line(self,x,y):
        if not self.tool_down:raise RuntimeError("linear route requires tool down")
        self.points.append((float(x),float(y)))
    def raise_tool(self):
        if not self.tool_down:raise RuntimeError("route tool is not down")
        self.tool_down=False
        pts=tuple(self.points)
        self.points=[pts[-1]] if pts else []
        self.positioned=bool(pts)
        return pts
