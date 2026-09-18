from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.roundtrip.invariants import board_invariants,compare_invariants
from photonx_eda_pcb.roundtrip.canonicalize import canonical_board_dict

def test_slot_invariants_and_canonicalization():
    a=BoardModel(slots=[SlotFeature("S",(0,0),(2,0),.8,"non-plated","T01")])
    b=BoardModel()
    assert board_invariants(a)["slots"]==1
    assert compare_invariants(a,b)["slots"]==(1,0)
    c=canonical_board_dict(a)
    assert c["slots"]==[{"id":"S","start":[0.0,0.0],"end":[2.0,0.0],"width_mm":.8,"plated":"non-plated","tool":"T01"}]
