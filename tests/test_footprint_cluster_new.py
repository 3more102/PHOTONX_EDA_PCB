from photonx_eda_pcb.models import *
from photonx_eda_pcb.footprints.clustering import cluster_pads

def test_cluster_separation():
 pads=[PadCandidate('a',Point(0,0),1,1,'C','F.Cu'),PadCandidate('b',Point(1,0),1,1,'C','F.Cu'),PadCandidate('c',Point(20,0),1,1,'C','F.Cu')]; assert sorted(map(len,cluster_pads(pads,2)))==[1,2]
