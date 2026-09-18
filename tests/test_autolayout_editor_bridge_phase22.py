from photonx_eda_pcb.schematic_editor import EditorDocument,EditorPage,EditorSymbol
from photonx_eda_pcb.schematic_autolayout.model import AutoLayoutResult
from photonx_eda_pcb.schematic_autolayout.editor_bridge import apply_to_editor
def test_autolayout_moves_editor_symbols():
    d=EditorDocument({"p":EditorPage("p","P")},{"s":EditorSymbol("s","U1","Device:R","R1","1k",0,0,page_id="p")})
    d.pages["p"].symbol_ids=["s"]
    moved=apply_to_editor(d,AutoLayoutResult("p",{"U1":(25,30)},[],0),{"U1":"s"})
    assert moved==["s"] and (d.symbols["s"].x,d.symbols["s"].y)==(25,30)
