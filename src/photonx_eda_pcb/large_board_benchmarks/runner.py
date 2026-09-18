from photonx_eda_pcb.stress_corpus import grid_board
from photonx_eda_pcb.benchmark_comparisons import benchmark_connectivity_paths,comparison_summary
from photonx_eda_pcb.connectivity.spatial_metrics import connectivity_candidate_metrics
def run_connectivity_scenario(scenario):
    board=grid_board(scenario.rows,scenario.cols,pitch_mm=scenario.pitch_mm)
    brute,spatial=benchmark_connectivity_paths(board,scenario.iterations)
    return {"scenario":scenario.name,"objects":len(board.pads)+len(board.tracks),"candidate_metrics":connectivity_candidate_metrics(board),"timing":comparison_summary(brute,spatial)}
