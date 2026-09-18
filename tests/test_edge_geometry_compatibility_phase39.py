from photonx_eda_pcb.models import BoardModel,OutlineSegment,Point
from photonx_eda_pcb.drc.edge import outline_geometry
def test_outline_geometry_keeps_boundary_outer_compatibility():
    pts=[Point(0,0),Point(5,0),Point(5,5),Point(0,5)]
    board=BoardModel(outline=[OutlineSegment(str(i),pts[i],pts[(i+1)%4]) for i in range(4)])
    boundary,outer=outline_geometry(board)
    assert boundary is not None and outer is not None and round(outer.area,6)==25.0
