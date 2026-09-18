from photonx_eda_pcb.models import BoardModel,PadCandidate,Point,NetGroup
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.roundtrip.mechanical import compare_mechanical_slots

def test_evidence_backed_plated_slot_exports_and_roundtrips(tmp_path):
    s=SlotFeature("S",(0,0),(4,0),1,"plated")
    pads=[
      PadCandidate("F",Point(2,0),6,2,"O","F.Cu",net_id="N1"),
      PadCandidate("B",Point(2,0),6,2,"O","B.Cu",net_id="N1"),
    ]
    b=BoardModel(pads=pads,slots=[s],nets=[NetGroup("N1",["F","B"],.99,"SIG")])
    path,report=export_kicad_with_report(b,tmp_path/"x.kicad_pcb")
    text=path.read_text()
    assert 'RecoveredPlatedSlot' in text and 'thru_hole oval' in text
    assert '(drill oval 5.000000 1.000000)' in text
    assert report.exported_plated_slots==1 and report.skipped_slots==0
    parsed=read_kicad_board_text(text)
    assert parsed["mechanical_slots"][0].plated=="plated"
    assert compare_mechanical_slots([s],parsed["mechanical_slots"])["equal"]
