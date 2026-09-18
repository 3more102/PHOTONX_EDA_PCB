from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.plated_slot_inference import infer_plated_slot_padstack

def board(net_a="N1",net_b="N1",size_b=(6,2)):
    slot=SlotFeature("S",(0,0),(4,0),1.0,"plated")
    pads=[
      PadCandidate("F",Point(2,0),6,2,"O","F.Cu",net_id=net_a),
      PadCandidate("B",Point(2,0),size_b[0],size_b[1],"O","B.Cu",net_id=net_b),
    ]
    return BoardModel(pads=pads,slots=[slot]),slot

def test_consistent_multilayer_copper_proves_exportable_padstack():
    b,s=board();r=infer_plated_slot_padstack(b,s)
    assert r.padstack is not None,r.blockers
    p=r.padstack
    assert p.layers==("F.Cu","B.Cu") and p.net_id=="N1"
    assert p.pad_size==(6.0,2.0) and p.drill_size==(5.0,1.0)
    assert p.confidence==.95

def test_net_conflict_blocks_padstack():
    b,s=board("N1","N2");r=infer_plated_slot_padstack(b,s)
    assert r.padstack is None and "SLOT_PAD_NET_CONFLICT" in r.blockers

def test_pad_size_conflict_blocks_padstack():
    b,s=board(size_b=(7,2));r=infer_plated_slot_padstack(b,s)
    assert r.padstack is None and "SLOT_PAD_SIZE_CONFLICT" in r.blockers
