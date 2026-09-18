import networkx as nx
def dependency_graph(dependencies):
    g=nx.DiGraph()
    for d in dependencies:g.add_edge(d.upstream,d.downstream,component=d.via_component,confidence=d.confidence)
    return g
