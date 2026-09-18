from photonx_eda_pcb.compatibility_matrix.model import CompatibilityMatrix,CompatibilityEntry
from photonx_eda_pcb.compatibility_freeze import evaluate_compatibility_freeze
def test_supported_tested_matrix_can_freeze():
    m=CompatibilityMatrix([CompatibilityEntry("linear","gerber","supported","",("test_linear",))])
    assert evaluate_compatibility_freeze(m,[]).passed
