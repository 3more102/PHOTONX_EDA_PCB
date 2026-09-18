def add_slot_layer_edges(graph,candidate):
    nodes=[f"{candidate.slot_id}@{layer}" for layer in candidate.layers]
    for n in nodes:graph.add_node(n)
    if candidate.proven and not candidate.conflict:
        for a,b in zip(nodes,nodes[1:]):graph.add_edge(a,b)
    return tuple(nodes)
