from photonx_eda_pcb.polarity_orientation.model import PolarityCandidate
from photonx_eda_pcb.polarity_orientation.conflicts import polarity_conflict
def test_polarity_conflict():
    a=PolarityCandidate("D","1","2",.8);b=PolarityCandidate("D","2","1",.8)
    assert polarity_conflict(a,b)
