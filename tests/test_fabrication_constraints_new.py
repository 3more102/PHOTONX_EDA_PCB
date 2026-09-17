from photonx_eda_pcb.fabrication_constraints.model import FabricationRules
from photonx_eda_pcb.fabrication_constraints.checks import evaluate_constraints

def test_fab_constraint_detection():
    r=FabricationRules(min_track_mm=.2,min_clearance_mm=.2,min_drill_mm=.3,min_annular_mm=.1)
    issues=evaluate_constraints({'min_track_mm':.1,'min_clearance_mm':.25,'min_drill_mm':.3,'min_annular_mm':.1},r)
    assert issues==['FAB_TRACK_TOO_SMALL']
