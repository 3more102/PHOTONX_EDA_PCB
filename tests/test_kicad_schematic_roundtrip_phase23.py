from photonx_eda_pcb.schematic_editor import *
from photonx_eda_pcb.schematic_editor.pages import ensure_page
from photonx_eda_pcb.kicad_schematic_export import export_document_from_editor,write_export_document
from photonx_eda_pcb.kicad_schematic_roundtrip import read_schematic_text,validate_roundtrip_read
from photonx_eda_pcb.kicad_schematic_roundtrip.stats import schematic_stats
def test_export_parse_roundtrip_counts():
    d=EditorDocument();ensure_page(d,"root")
    add_object(d,EditorSymbol("s1","U1","Device:R","R1","10k",10,20))
    add_object(d,EditorLabel("l1","N1","VCC",15,20,global_label=True))
    data=read_schematic_text(write_export_document(export_document_from_editor(d,"Demo")))
    assert schematic_stats(data)=={"symbols":1,"wires":0,"labels":0,"global_labels":1}
    assert validate_roundtrip_read(data)==[]
