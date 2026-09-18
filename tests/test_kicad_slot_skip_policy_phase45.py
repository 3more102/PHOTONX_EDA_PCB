from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report

def test_unknown_and_plated_slots_are_not_fabricated(tmp_path):
    b=BoardModel(slots=[
      SlotFeature("U",(0,0),(1,0),.5,"unknown"),
      SlotFeature("P",(0,1),(1,1),.5,"plated"),
    ])
    p,r=export_kicad_with_report(b,tmp_path/"x.kicad_pcb")
    text=p.read_text()
    assert 'RecoveredNPTHSlot' not in text
    assert r.exported_slots==0 and r.skipped_slots==2
    assert {x.code for x in r.issues}=={"KICAD_SLOT_PLATING_UNKNOWN","KICAD_SLOT_PLATED_UNSUPPORTED"}
