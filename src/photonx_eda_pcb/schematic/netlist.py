def component_net_map(board):
    member_net={m:n.id for n in board.nets for m in n.members}; return {c.id:[member_net.get(p) for p in c.pad_ids] for c in board.components}
def unresolved_component_pins(board): return {cid:[i for i,n in enumerate(nets,1) if n is None] for cid,nets in component_net_map(board).items() if any(n is None for n in nets)}
