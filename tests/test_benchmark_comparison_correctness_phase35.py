from photonx_eda_pcb.stress_corpus import grid_board
from photonx_eda_pcb.connectivity.graph import build_physical_graph,build_physical_graph_bruteforce
from photonx_eda_pcb.benchmark_comparisons.correctness import graph_equivalent
def test_benchmark_paths_have_same_graph():
    b=grid_board(8,8,pitch_mm=1.2)
    assert graph_equivalent(build_physical_graph_bruteforce(b),build_physical_graph(b))
