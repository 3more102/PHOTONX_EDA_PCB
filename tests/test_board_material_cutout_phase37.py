from photonx_eda_pcb.models import BoardModel,OutlineSegment,Point
from photonx_eda_pcb.board_material_geometry import board_material_shape,validate_material_shape
from photonx_eda_pcb.board_material_geometry.report import material_report
def loop(prefix,pts):
    return [OutlineSegment(prefix+str(i),Point(*pts[i]),Point(*pts[(i+1)%len(pts)])) for i in range(len(pts))]
def test_board_material_subtracts_cutout():
    outer=[(0,0),(10,0),(10,10),(0,10)];inner=[(4,4),(6,4),(6,6),(4,6)]
    b=BoardModel(outline=loop("o",outer)+loop("i",inner))
    s=board_material_shape(b)
    assert round(s.area,6)==96.0 and validate_material_shape(s)==[]
    r=material_report(b);assert r["cutouts"]>=1 and r["holes"]>=1
