from photonx_eda_pcb.models import PadCandidate,Point,BoardModel
from photonx_eda_pcb.drc.annular import annular_ring_mm,check_annular_ring
from photonx_eda_pcb.drc.model import DrcConfig
def test_drill_larger_than_pad_is_broken_ring():
    p=PadCandidate("P",Point(0,0),1,1,"C","F.Cu",drill=1.2)
    assert annular_ring_mm(p)<0
    assert any(x.code=="ANNULAR_RING_BROKEN" for x in check_annular_ring(BoardModel(pads=[p]),DrcConfig()))
