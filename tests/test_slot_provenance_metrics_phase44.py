from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.provenance import Provenance,SourceRef
from photonx_eda_pcb.analysis.provenance_metrics import source_coverage

def test_slot_contributes_to_source_coverage():
    s=SlotFeature("S",(0,0),(1,0),.5,"unknown",None,Provenance([SourceRef("a.drl",1,"G85")],[]))
    assert source_coverage(BoardModel(slots=[s]))==1.0
