from types import SimpleNamespace
from photonx_eda_pcb.board_query.selectors import select_by_layer,select_by_net
from photonx_eda_pcb.board_query.summary import board_object_counts
def test_board_query_helpers():
    p=SimpleNamespace(layer="F.Cu",net_id="N1")
    b=SimpleNamespace(tracks=[],pads=[p],drills=[],components=[],nets=[1])
    assert select_by_layer(b,"F.Cu")==[p] and select_by_net(b,"N1")==[p]
    assert board_object_counts(b)["pads"]==1
