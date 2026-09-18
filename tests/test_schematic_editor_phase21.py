from photonx_eda_pcb.schematic_editor import *
from photonx_eda_pcb.schematic_editor.pages import ensure_page
def test_editor_add_move_remove():
    d=EditorDocument();ensure_page(d,"root","Root")
    s=EditorSymbol("s1","U1","Device:R","R1","10k",0,0,confidence=.8)
    add_object(d,s);assert d.pages["root"].symbol_ids==["s1"]
    moved=move_symbol(d,"s1",10,20,90);assert (moved.x,moved.y,moved.rotation)==(10,20,90)
    assert validate_document(d)==[]
    assert remove_object(d,"s1").reference=="R1" and not d.symbols
