def net_degrees(board):
    component_by_pad={p:c.id for c in board.components for p in c.pad_ids}; out={}
    for n in board.nets:out[n.id]=len({component_by_pad[m] for m in n.members if m in component_by_pad})
    return out
def dangling_nets(board): return [n for n,d in net_degrees(board).items() if d<=1]
