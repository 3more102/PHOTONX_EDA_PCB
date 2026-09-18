from photonx_eda_pcb.stress_corpus import grid_board
from photonx_eda_pcb.connectivity.spatial_metrics import connectivity_candidate_metrics
def test_sparse_grid_reduces_candidate_pairs():
    b=grid_board(20,20,pitch_mm=3.0,pad_mm=.5)
    m=connectivity_candidate_metrics(b,.03)
    assert m["same_layer_bruteforce_pairs"]>m["spatial_candidate_pairs"]
    assert m["reduction_ratio"]>.5
