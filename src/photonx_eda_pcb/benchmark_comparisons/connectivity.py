from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.connectivity.graph import build_physical_graph,build_physical_graph_bruteforce

def benchmark_connectivity_paths(board,iterations=1):
    brute=benchmark("connectivity_bruteforce",lambda:build_physical_graph_bruteforce(board),iterations=iterations,warmup=0)
    spatial=benchmark("connectivity_spatial",lambda:build_physical_graph(board),iterations=iterations,warmup=0)
    return brute,spatial
