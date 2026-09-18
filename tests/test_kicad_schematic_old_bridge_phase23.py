from photonx_eda_pcb.schematic_editor import EditorDocument,EditorPage,EditorSymbol
from photonx_eda_pcb.kicad_schematic.structured import write_editor_schematic
def test_old_package_structured_bridge():
    d=EditorDocument({"root":EditorPage("root","Root")},{"s":EditorSymbol("s","U1","Device:R","R1","1k",0,0,page_id="root")})
    d.pages["root"].symbol_ids=["s"]
    assert write_editor_schematic(d,"Demo").startswith("(kicad_sch")
