from photonx_eda_pcb.models import PadCandidate,Point
from photonx_eda_pcb.footprints.clustering import cluster_pads,cluster_pads_bruteforce
def pads():
    return [PadCandidate("A",Point(0,0),.5,.5,"C","F.Cu"),PadCandidate("B",Point(1,0),.5,.5,"C","F.Cu"),PadCandidate("C",Point(10,0),.5,.5,"C","F.Cu"),PadCandidate("D",Point(11,0),.5,.5,"C","F.Cu")]
def sig(groups):return [[p.id for p in g] for g in groups]
def test_footprint_cluster_spatial_parity():
    assert sig(cluster_pads_bruteforce(pads(),2))==sig(cluster_pads(pads(),2))
    assert sig(cluster_pads(pads(),2))==[["A","B"],["C","D"]]
