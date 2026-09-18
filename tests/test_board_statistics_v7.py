from photonx_eda_pcb.models import BoardModel,Point,Track,OutlineSegment
from photonx_eda_pcb.board_statistics import compute_board_stats,validate_stats
def test_board_statistics():
    b=BoardModel(tracks=[Track("t",Point(0,0),Point(3,4),.2,"F.Cu")],outline=[OutlineSegment("o1",Point(0,0),Point(10,0)),OutlineSegment("o2",Point(10,0),Point(10,5))])
    s=compute_board_stats(b)
    assert s.tracks==1 and s.total_track_length_mm==5.0 and s.board_width_mm==10 and s.board_height_mm==5
    assert validate_stats(s)==[]
