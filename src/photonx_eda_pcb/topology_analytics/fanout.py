def component_fanout(graph,component_id):
    node="C:"+str(component_id)
    return len(set(graph.neighbors(node))) if node in graph else 0
