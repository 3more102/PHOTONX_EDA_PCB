from photonx_eda_pcb.models import BoardModel,OutlineSegment,Point
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.drc.edge import check_edge_presence
from photonx_eda_pcb.drc.model import DrcConfig

def outline(w=10,h=10):
    pts=[Point(0,0),Point(w,0),Point(w,h),Point(0,h)]
    return [OutlineSegment(str(i),pts[i],pts[(i+1)%4]) for i in range(4)]

def test_slot_near_edge_is_reported():
    b=BoardModel(outline=outline(),slots=[SlotFeature("S",(.3,2),(2,2),.4,"non-plated")])
    issues=check_edge_presence(b,DrcConfig(edge_clearance_mm=.2))
    assert any(x.code=="SLOT_EDGE_CLEARANCE" for x in issues)

def test_slot_crossing_edge_is_outside():
    b=BoardModel(outline=outline(),slots=[SlotFeature("S",(-1,2),(1,2),.4,"non-plated")])
    issues=check_edge_presence(b,DrcConfig())
    assert any(x.code=="SLOT_OUTSIDE_BOARD" for x in issues)
