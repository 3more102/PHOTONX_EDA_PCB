from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.plated_slot_inference import infer_plated_slot_padstack

def test_single_layer_copper_is_not_enough_for_plated_export():
    s=SlotFeature("S",(0,0),(4,0),1,"plated")
    b=BoardModel(pads=[PadCandidate("F",Point(2,0),6,2,"O","F.Cu")],slots=[s])
    r=infer_plated_slot_padstack(b,s)
    assert r.padstack is None
    assert "SLOT_PADSTACK_NEEDS_MULTILAYER_EVIDENCE" in r.blockers
