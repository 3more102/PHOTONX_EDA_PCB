from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.mechanical_features.export_readiness import assess_board_slot_export_readiness

def test_board_readiness_recognizes_resolved_plated_slot():
    s=SlotFeature("S",(0,0),(4,0),1,"plated")
    b=BoardModel(pads=[
      PadCandidate("F",Point(2,0),6,2,"O","F.Cu"),
      PadCandidate("B",Point(2,0),6,2,"O","B.Cu"),
    ],slots=[s])
    r=assess_board_slot_export_readiness(b)
    assert r.exportable_plated==("S",) and not r.plated_without_padstack
