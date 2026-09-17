from photonx_eda_pcb.zones.model import Zone
from photonx_eda_pcb.fabrication_constraints.profiles import DEFAULT_RULES
from photonx_eda_pcb.cross_source_validation.scoring import source_weight
from photonx_eda_pcb.fuzzing.limits import within_limits

def test_expansion3_import_surface():
    assert Zone('z','F.Cu').layer=='F.Cu'
    assert DEFAULT_RULES.min_track_mm>0
    assert source_weight('ipc356')>source_weight('silkscreen')
    assert within_limits('x')
