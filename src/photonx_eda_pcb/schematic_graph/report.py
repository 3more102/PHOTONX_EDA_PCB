def graph_summary(g):
    return {"components":len(g.components),"nets":len(g.nets),"pin_edges":len(g.pin_edges)}
