from photonx_eda_pcb.compatibility_matrix import CompatibilityEntry,CompatibilityMatrix
from photonx_eda_pcb.compatibility_matrix.merge import merge_matrices
def test_merge_prefers_higher_status():
    a=CompatibilityMatrix([CompatibilityEntry("x","gerber","partial")]);b=CompatibilityMatrix([CompatibilityEntry("x","gerber","supported")])
    assert merge_matrices(a,b).entries[0].status=="supported"
