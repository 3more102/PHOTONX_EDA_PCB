def high_degree_nodes(graph,min_degree=4):
    return sorted([(n,int(d)) for n,d in graph.degree() if d>=int(min_degree)],key=lambda x:(-x[1],x[0]))
