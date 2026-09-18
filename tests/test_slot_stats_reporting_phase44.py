from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.analysis.board_stats import board_stats
from photonx_eda_pcb.reporting import summary

def test_slots_in_stats_and_legacy_summary():
    b=BoardModel(slots=[SlotFeature("S",(0,0),(1,0),.5)])
    assert board_stats(b)["slots"]==1
    assert summary(b)["slots"]==1
