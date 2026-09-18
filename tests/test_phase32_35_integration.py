from photonx_eda_pcb.stress_corpus import clustered_board
from photonx_eda_pcb.connectivity.spatial_metrics import connectivity_candidate_metrics
from photonx_eda_pcb.footprints.clustering import cluster_pads
from photonx_eda_pcb.inference.components import infer_component_hypotheses
def test_spatialized_reconstruction_flow():
    b=clustered_board(4,10,spacing_mm=20,local_pitch_mm=.4)
    assert connectivity_candidate_metrics(b,.03)["reduction_ratio"]>0
    groups=cluster_pads(b.pads,1.0)
    assert len(groups)==4
    comps=infer_component_hypotheses(b,1.0)
    assert comps and len(comps)<=len(b.pads)
