from .model import DrcIssue

def check_edge_presence(board,cfg):
    return [] if board.outline else [DrcIssue('warning','BOARD_OUTLINE_MISSING','edge clearance cannot be evaluated without outline')]
