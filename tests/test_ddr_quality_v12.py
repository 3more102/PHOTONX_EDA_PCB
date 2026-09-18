from photonx_eda_pcb.ddr_topology import infer_ddr_topology
from photonx_eda_pcb.ddr_topology.quality import topology_completeness,lane_counts
def test_ddr_completeness():
    t=infer_ddr_topology({"d0":"DQ0","a0":"A0","ck":"CKP"})
    assert topology_completeness(t)==1.0
    assert lane_counts(t)["data"]==1
