from photonx_eda_pcb.models import BoardModel,Track,Point
from photonx_eda_pcb.gui_arch.view_model import board_view_model
def test_vm():
    b=BoardModel(tracks=[Track('t',Point(0,0),Point(1,0),.2,'F.Cu')]); v=board_view_model(b); assert v['counts']['tracks']==1 and v['layers']==['F.Cu']
