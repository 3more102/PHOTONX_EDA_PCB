from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature

def test_board_model_serializes_and_indexes_slots():
    s=SlotFeature("S",(0,0),(2,0),.8)
    b=BoardModel(slots=[s])
    assert b.object_index()["S"]==s
    d=b.to_dict()
    assert d["slots"][0]["id"]=="S" and d["slots"][0]["width_mm"]==.8
