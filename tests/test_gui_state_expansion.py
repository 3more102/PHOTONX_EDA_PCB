from photonx_eda_pcb.gui_arch.state import AppState
from photonx_eda_pcb.gui_arch.controller import AppController
def test_state():
    s=AppState(); c=AppController(s); c.dispatch('select',{'id':'p1'}); c.dispatch('zoom',{'factor':2}); assert s.selected_id=='p1' and s.zoom==2
