import networkx as nx
from .graph import sequence_graph
def topological_order(items):
    g=sequence_graph(items)
    return tuple(nx.topological_sort(g)) if nx.is_directed_acyclic_graph(g) else ()
