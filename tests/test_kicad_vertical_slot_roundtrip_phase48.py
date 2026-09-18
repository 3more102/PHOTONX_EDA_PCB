from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.roundtrip.mechanical import compare_mechanical_slots

def test_vertical_slot_roundtrip(tmp_path):
    board=BoardModel(slots=[SlotFeature("S",(3,1),(3,5),.8,"non-plated")])
    path,_=export_kicad_with_report(board,tmp_path/"x.kicad_pcb")
    parsed=read_kicad_board_text(path.read_text())
    assert compare_mechanical_slots(board.slots,parsed["mechanical_slots"])["equal"]
