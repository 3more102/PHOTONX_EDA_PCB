def validate_layer_graph(graph):
    issues=[]
    for node in graph.nodes():
        if node in graph.neighbors(node): issues.append(("error","SELF_EDGE",node))
        for neighbor in graph.neighbors(node):
            if node not in graph.neighbors(neighbor): issues.append(("error","ASYMMETRIC_EDGE",node,neighbor))
    return issues
