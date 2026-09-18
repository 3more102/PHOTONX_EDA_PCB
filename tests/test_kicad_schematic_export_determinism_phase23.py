from photonx_eda_pcb.schematic_editor import EditorDocument,EditorPage,EditorSymbol
from photonx_eda_pcb.kicad_schematic_export import export_document_from_editor,write_export_document
def test_structured_export_deterministic():
    d=EditorDocument({"root":EditorPage("root","Root")},{"s":EditorSymbol("s","U1","Device:C","C1","100n",10,10,page_id="root")})
    d.pages["root"].symbol_ids=["s"]
    a=write_export_document(export_document_from_editor(d,"Demo"));b=write_export_document(export_document_from_editor(d,"Demo"))
    assert a==b
