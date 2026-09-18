def validate_topology_graph(graph):
    return ["TOPOLOGY_SELF_LOOP"] if any(a==b for a,b in graph.edges()) else []
