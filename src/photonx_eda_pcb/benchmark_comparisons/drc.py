from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.drc.clearance import check_clearance,check_clearance_bruteforce
from photonx_eda_pcb.drc.model import DrcConfig

def benchmark_clearance_paths(board,cfg=None,iterations=1):
    cfg=cfg or DrcConfig()
    brute=benchmark("clearance_bruteforce",lambda:check_clearance_bruteforce(board,cfg),iterations=iterations,warmup=0)
    spatial=benchmark("clearance_spatial",lambda:check_clearance(board,cfg),iterations=iterations,warmup=0)
    return brute,spatial
