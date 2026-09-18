def component_degree(graph,component_id):
    return sum(1 for c,_,_ in graph.pin_edges if c==component_id)
def net_degree(graph,net_id):
    return sum(1 for _,_,n in graph.pin_edges if n==net_id)
