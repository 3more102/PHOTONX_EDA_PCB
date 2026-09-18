from photonx_eda_pcb.stress_corpus import clustered_board
from photonx_eda_pcb.connectivity.spatial_metrics import connectivity_candidate_metrics
def test_clustered_spatial_metrics_still_reduce_global_pairs():
    b=clustered_board(10,20,spacing_mm=20)
    m=connectivity_candidate_metrics(b,.03,cell_size_mm=1)
    assert m["spatial_candidate_pairs"]<m["same_layer_bruteforce_pairs"]
