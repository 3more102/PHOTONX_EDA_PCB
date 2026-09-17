from photonx_eda_pcb.gui_arch.state import AppState
from photonx_eda_pcb.gui_arch.layer_state import toggle_layer
def test_layer():
    s=AppState(); toggle_layer(s,'F.Cu'); assert 'F.Cu' in s.visible_layers; toggle_layer(s,'F.Cu'); assert 'F.Cu' not in s.visible_layers
