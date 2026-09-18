def validate_graph(graph):
    issues=[]
    for e in graph.edges:
        if e.source not in graph.nodes or e.target not in graph.nodes:issues.append("PROVENANCE_EDGE_UNKNOWN_NODE")
        if not 0<=e.confidence<=1:issues.append("PROVENANCE_EDGE_CONFIDENCE_RANGE")
    return issues
