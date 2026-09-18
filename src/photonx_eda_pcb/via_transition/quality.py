from .annular import annular_ring_mm
from .return_support import return_support_score
from .stub import stub_penalty
def transition_quality(v,total_layers=2,min_annular_mm=.1):
    ann=min(1.0,annular_ring_mm(v.pad_mm,v.drill_mm)/max(float(min_annular_mm),1e-9))
    score=.45*ann+.35*return_support_score(v.nearby_return_vias)+.2*(1-stub_penalty(v.stub_layers,total_layers))
    return round(min(1.0,max(0.0,score)),6)
