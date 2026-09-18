from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report

def test_unresolved_plated_slot_keeps_legacy_issue_code(tmp_path):
    _,report=export_kicad_with_report(BoardModel(slots=[SlotFeature("S",(0,0),(1,0),.5,"plated")]),tmp_path/"x.kicad_pcb")
    assert report.issues[0].code=="KICAD_SLOT_PLATED_UNSUPPORTED"
    assert "SLOT_NO_COPPER_PAD_COVERAGE" in report.issues[0].message
