from photonx_eda_pcb.schematic_editor import *
from photonx_eda_pcb.schematic_editor.pages import ensure_page
from photonx_eda_pcb.schematic_canvas import hit_test,snap_point
from photonx_eda_pcb.schematic_canvas.bounds import page_bounds
def test_canvas_hit_snap_bounds():
    d=EditorDocument();ensure_page(d,"root")
    add_object(d,EditorSymbol("s","U1","Device:R","R1","10k",10,20))
    assert hit_test(d,"root",10,20)==("s",)
    assert snap_point((2.6,5.0),2.54)==(2.54,5.08)
    b=page_bounds(d,"root");assert b[0]<10<b[2] and b[1]<20<b[3]
