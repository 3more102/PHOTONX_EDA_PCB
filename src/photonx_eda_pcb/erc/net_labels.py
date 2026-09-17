from .model import ErcIssue
def check_labels(board): return [ErcIssue('info','NET_LABEL_UNKNOWN','physical net has no semantic label',n.id) for n in board.nets if n.label is None]
