from photonx_eda_pcb.stress_corpus import grid_board
from photonx_eda_pcb.benchmark_comparisons import benchmark_connectivity_paths,comparison_summary
def test_benchmark_comparison_smoke():
    brute,spatial=benchmark_connectivity_paths(grid_board(6,6,pitch_mm=2),iterations=1)
    s=comparison_summary(brute,spatial)
    assert s["bruteforce_seconds"]>=0 and s["spatial_seconds"]>=0
