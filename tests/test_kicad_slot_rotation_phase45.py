from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report

def test_vertical_slot_exports_rotation(tmp_path):
    b=BoardModel(slots=[SlotFeature("S",(2,1),(2,5),1.0,"non-plated")])
    p,_=export_kicad_with_report(b,tmp_path/"slot.kicad_pcb")
    text=p.read_text()
    assert '(at 0 0 90.000000)' in text
    assert '(at 2.000000 3.000000)' in text
