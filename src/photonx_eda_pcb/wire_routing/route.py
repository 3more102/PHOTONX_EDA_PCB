from .model import WireRoute
from .manhattan import manhattan_points
def route_manhattan(net_id,start,end,prefer_horizontal=True):return WireRoute(str(net_id),manhattan_points(start,end,prefer_horizontal),"manhattan",1.0)
