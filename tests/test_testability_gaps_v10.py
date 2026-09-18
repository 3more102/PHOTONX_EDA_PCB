from photonx_eda_pcb.testpoints.model import TestPointCandidate
from photonx_eda_pcb.testability_analysis.gaps import untested_nets
def test_untested_nets():
    t=[TestPointCandidate("t","n1",1,True,.9,[])]
    assert untested_nets(["n1","n2"],t)==["n2"]
