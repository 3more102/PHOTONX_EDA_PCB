from photonx_eda_pcb.models import BoardModel,Point,OutlineSegment
from photonx_eda_pcb.drc.edge import check_edge_presence
from photonx_eda_pcb.drc.model import DrcConfig
def test_open_outline_reports_unclosed():
    b=BoardModel(outline=[OutlineSegment("a",Point(0,0),Point(1,0))])
    x=check_edge_presence(b,DrcConfig())
    assert [i.code for i in x]==["BOARD_OUTLINE_NOT_CLOSED"]
