from photonx_eda_pcb.schematic_editor import *
from photonx_eda_pcb.schematic_editor.pages import ensure_page
from photonx_eda_pcb.schematic_editor.serialize import dumps_document,loads_document
def test_editor_json_roundtrip():
    d=EditorDocument();ensure_page(d,"root","Root")
    add_object(d,EditorSymbol("s","U","Device:C","C1","100n",1,2,confidence=.7))
    add_object(d,EditorWire("w","N1",((1,2),(5,2))))
    add_object(d,EditorLabel("l","N1","VCC",5,2))
    q=loads_document(dumps_document(d))
    assert q.symbols==d.symbols and q.wires==d.wires and q.labels==d.labels
