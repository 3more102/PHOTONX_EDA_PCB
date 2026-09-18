import networkx as nx
def sequence_graph(items):
    g=nx.DiGraph()
    for x in items:g.add_edge(x.before,x.after,reason=x.reason,confidence=x.confidence)
    return g
