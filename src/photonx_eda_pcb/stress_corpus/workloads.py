from photonx_eda_pcb.connectivity.graph import build_physical_graph
from photonx_eda_pcb.drc.engine import run_drc
from photonx_eda_pcb.drc.model import DrcConfig
def connectivity_workload(board):
    return lambda:build_physical_graph(board)
def drc_workload(board,cfg=None):
    return lambda:run_drc(board,cfg or DrcConfig())
