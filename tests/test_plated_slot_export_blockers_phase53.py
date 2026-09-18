from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report

def test_plated_slot_with_conflicting_nets_is_skipped(tmp_path):
    s=SlotFeature("S",(0,0),(4,0),1,"plated")
    b=BoardModel(pads=[
      PadCandidate("F",Point(2,0),6,2,"O","F.Cu",net_id="A"),
      PadCandidate("B",Point(2,0),6,2,"O","B.Cu",net_id="B"),
    ],slots=[s])
    p,r=export_kicad_with_report(b,tmp_path/"x.kicad_pcb")
    assert 'RecoveredPlatedSlot' not in p.read_text()
    assert r.skipped_slot_ids==["S"]
    issue=r.issues[0]
    assert issue.code=="KICAD_SLOT_PLATED_PADSTACK_UNRESOLVED"
    assert "SLOT_PAD_NET_CONFLICT" in issue.message
