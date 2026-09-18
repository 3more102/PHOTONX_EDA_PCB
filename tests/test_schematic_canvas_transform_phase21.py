from photonx_eda_pcb.gui_interaction.viewport import Viewport
from photonx_eda_pcb.schematic_canvas.transform import world_to_screen,screen_to_world
def test_canvas_transform_roundtrip():
    v=Viewport(10,20,2)
    p=(15,25);s=world_to_screen(p,v,1000,500);q=screen_to_world(s,v,1000,500)
    assert q==p
