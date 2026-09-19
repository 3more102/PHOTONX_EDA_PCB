import pytest
from photonx_eda_pcb.models import Point,BoardModel,Track,PadCandidate
from photonx_eda_pcb.geometry.bbox import bounds_from_points,board_bounds
from photonx_eda_pcb.geometry.segment import segment_length,point_to_segment_distance
from photonx_eda_pcb.geometry.transforms import rotate,translate
from photonx_eda_pcb.geometry.grid import quantize_point
from photonx_eda_pcb.geometry.polygon import signed_area
def test_bounds_and_length():
 b=bounds_from_points([Point(1,2),Point(4,6)]); assert (b.width,b.height)==(3,4); assert segment_length(Point(0,0),Point(3,4))==5
def test_point_segment_distance(): assert point_to_segment_distance(Point(1,1),Point(0,0),Point(2,0))==pytest.approx(1)
def test_transforms():
 q=rotate(Point(1,0),90); assert q.x==pytest.approx(0,abs=1e-9) and q.y==pytest.approx(1); assert translate(Point(1,2),3,4)==Point(4,6)
def test_grid_and_area(): assert quantize_point(Point(1.24,2.26),0.1)==Point(1.2,2.3); assert signed_area([Point(0,0),Point(2,0),Point(2,2),Point(0,2)])==4
def test_board_bounds():
 board=BoardModel(tracks=[Track("T0",Point(0,0),Point(5,0),.2,"F.Cu")],pads=[PadCandidate("P0",Point(2,3),1,1,"C","F.Cu")]); b=board_bounds(board); assert b.max_y==pytest.approx(3.5) and b.max_x==pytest.approx(5.1)
