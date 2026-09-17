from ..models import BoardModel
def net_member_counts(board:BoardModel)->dict[str,int]: return {n.id:len(n.members) for n in board.nets}
def low_confidence_nets(board:BoardModel,threshold:float=0.5): return [n.id for n in board.nets if n.confidence<threshold]
def labeled_net_fraction(board:BoardModel)->float: return 0.0 if not board.nets else sum(n.label is not None for n in board.nets)/len(board.nets)
