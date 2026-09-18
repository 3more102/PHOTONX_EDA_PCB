def graph_summary(graph):
    kinds={}
    for n in graph.nodes.values():kinds[n.kind]=kinds.get(n.kind,0)+1
    return {"nodes":len(graph.nodes),"edges":len(graph.edges),"kinds":dict(sorted(kinds.items()))}
