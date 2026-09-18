from photonx_eda_pcb.compatibility_matrix import CompatibilityEntry,CompatibilityMatrix,compatibility_for,validate_matrix
from photonx_eda_pcb.compatibility_matrix.coverage import compatibility_score
def test_compatibility_matrix():
    m=CompatibilityMatrix([CompatibilityEntry("arcs","gerber","supported"),CompatibilityEntry("slots","excellon","partial")])
    assert compatibility_for(m,format="gerber")[0].feature=="arcs"
    assert compatibility_score(m)>.5 and validate_matrix(m)==[]
