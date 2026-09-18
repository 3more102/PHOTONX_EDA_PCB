from photonx_eda_pcb.gui_interaction import Viewport,SelectionState,LayerVisibility
from photonx_eda_pcb.gui_controllers import ViewportController,SelectionController,LayerController
def test_gui_controllers():
    v=ViewportController(Viewport());v.fit_bounds((0,0,100,50),1000,500)
    assert v.viewport.zoom>0
    s=SelectionController(SelectionState());s.add("P1");assert s.state.primary=="P1"
    l=LayerController(LayerVisibility());l.hide("F.Cu");assert not l.state.is_visible("F.Cu")
