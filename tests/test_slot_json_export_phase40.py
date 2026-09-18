import json
from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.exporters.json_export import export_json

def test_json_export_includes_slots(tmp_path):
    p=export_json(BoardModel(slots=[SlotFeature("S",(0,0),(1,0),.5)]),tmp_path/"board.json")
    d=json.loads(p.read_text())
    assert d["slots"][0]["id"]=="S"
