from photonx_eda_pcb.stress_corpus import grid_board
from photonx_eda_pcb.connectivity.graph import build_physical_graph
from photonx_eda_pcb.connectivity.spatial_metrics import connectivity_candidate_metrics
from photonx_eda_pcb.parser_conformance.library import builtin_cases
from photonx_eda_pcb.parser_conformance import run_conformance_suite
def test_deep_integration_spatial_and_conformance():
    b=grid_board(6,6,pitch_mm=1.0);g=build_physical_graph(b)
    assert g.number_of_nodes()==len(b.pads)+len(b.tracks)
    assert connectivity_candidate_metrics(b)["reduction_ratio"]>=0
    assert all(x.passed for x in run_conformance_suite(builtin_cases()))
