from photonx_eda_pcb.reporting import summary
from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature

def test_reporting_summary_compatibility_facade():
    data=summary(BoardModel(slots=[SlotFeature("S",(0,0),(1,0),.5)]))
    assert data["slots"]==1 and data["tracks"]==0
