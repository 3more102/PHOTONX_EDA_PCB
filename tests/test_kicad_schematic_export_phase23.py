from photonx_eda_pcb.schematic_editor import *
from photonx_eda_pcb.schematic_editor.pages import ensure_page
from photonx_eda_pcb.kicad_schematic_export import export_document_from_editor,write_export_document,validate_export_document
from photonx_eda_pcb.kicad_schematic_export.structural_validation import validate_text_structure
def test_structured_export():
    d=EditorDocument();ensure_page(d,"root")
    add_object(d,EditorSymbol("s1","R1","Device:R","R1","10k",25.4,25.4,confidence=.9))
    add_object(d,EditorWire("w1","N1",((25.4,25.4),(50.8,25.4))))
    add_object(d,EditorLabel("l1","N1","SIG",50.8,25.4))
    x=export_document_from_editor(d,"Demo")
    assert validate_export_document(x)==[]
    text=write_export_document(x)
    assert "(kicad_sch" in text and "(generator photonx)" in text and '"R1"' in text
    assert validate_text_structure(text)==[]
