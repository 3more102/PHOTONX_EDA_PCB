def add_via_span_edges(graph,via_id,layers):
    nodes=[f"{via_id}@{layer}" for layer in layers]
    for node in nodes: graph.add_node(node)
    for a,b in zip(nodes,nodes[1:]): graph.add_edge(a,b)
    return tuple(nodes)
