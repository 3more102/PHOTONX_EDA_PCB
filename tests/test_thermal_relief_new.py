from photonx_eda_pcb.thermal_relief.detection import infer_thermal
from photonx_eda_pcb.thermal_relief.symmetry import is_symmetric
from photonx_eda_pcb.thermal_relief.validation import validate_thermal
from photonx_eda_pcb.thermal_relief.scoring import thermal_confidence

def test_thermal_candidate_and_score():
    t=infer_thermal('P1','Z1',[0,90,180,270])
    assert is_symmetric(t.spokes)
    assert validate_thermal(t)==[]
    assert thermal_confidence(4,True,True,True)==1.0
