from photonx_eda_pcb.gui_interaction import Viewport
from photonx_eda_pcb.gui_interaction.coordinates import world_to_screen,screen_to_world
def test_coordinate_roundtrip():
    v=Viewport(10,5,2)
    s=world_to_screen(12,7,v,800,600)
    w=screen_to_world(*s,v,800,600)
    assert w==(12.0,7.0)
