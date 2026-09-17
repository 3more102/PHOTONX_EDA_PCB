def children(node,name):
    if not isinstance(node,list): return []
    return [x for x in node[1:] if isinstance(x,list) and x and x[0]==name]
def child(node,name):
    xs=children(node,name); return xs[0] if xs else None
