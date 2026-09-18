from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.roundtrip.kicad_text import kicad_text_counts

def test_nonplated_slot_exports_as_npth_oval_drill(tmp_path):
    b=BoardModel(slots=[SlotFeature("S",(0,0),(4,0),1.0,"non-plated")])
    p,r=export_kicad_with_report(b,tmp_path/"slot.kicad_pcb")
    text=p.read_text()
    assert 'np_thru_hole oval' in text
    assert '(drill oval 5.000000 1.000000)' in text
    counts=kicad_text_counts(text)
    assert counts["oval_drills"]==1 and counts["npth_pads"]==1
    assert r.exported_slots==1 and r.skipped_slots==0
