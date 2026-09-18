from photonx_eda_pcb.models import PadCandidate,Point,BoardModel
from photonx_eda_pcb.drc.annular import annular_ring_mm,check_annular_ring
from photonx_eda_pcb.drc.model import DrcConfig
def test_annular_ring_uses_exact_pad_boundary():
    p=PadCandidate("P",Point(0,0),4,2,"O","F.Cu",drill=1.0)
    assert round(annular_ring_mm(p),6)==.5
    assert check_annular_ring(BoardModel(pads=[p]),DrcConfig(min_annular_ring_mm=.4))==[]
