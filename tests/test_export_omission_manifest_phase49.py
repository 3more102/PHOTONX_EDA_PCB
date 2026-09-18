from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest,write_omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
import json

def test_omission_manifest_records_skipped_slots(tmp_path):
    board=BoardModel(slots=[SlotFeature("A",(0,0),(1,0),.5,"non-plated"),SlotFeature("B",(0,1),(1,1),.5,"unknown")])
    _,report=export_kicad_with_report(board,tmp_path/"b.kicad_pcb")
    data=omission_manifest(report)
    assert data["exported_slots"]==["A"] and data["skipped_slots"]==["B"]
    assert validate_omission_manifest(data)==[]
    p=write_omission_manifest(report,tmp_path/"omissions.json")
    assert json.loads(p.read_text())["skipped_slots"]==["B"]
