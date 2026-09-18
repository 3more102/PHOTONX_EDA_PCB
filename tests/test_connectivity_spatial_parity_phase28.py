from photonx_eda_pcb.stress_corpus import grid_board
from photonx_eda_pcb.connectivity.graph import build_physical_graph,build_physical_graph_bruteforce
def test_spatial_connectivity_matches_bruteforce():
    b=grid_board(8,8,pitch_mm=1.0,pad_mm=.8)
    a=build_physical_graph_bruteforce(b,.03);s=build_physical_graph(b,.03)
    assert sorted(map(tuple,map(sorted,a.edges())))==sorted(map(tuple,map(sorted,s.edges())))
    assert sorted(a.nodes())==sorted(s.nodes())
