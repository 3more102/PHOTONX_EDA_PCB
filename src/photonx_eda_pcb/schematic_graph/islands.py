def isolated_components(graph):
    connected={c for c,_,_ in graph.pin_edges}
    return sorted(set(graph.components)-connected)
