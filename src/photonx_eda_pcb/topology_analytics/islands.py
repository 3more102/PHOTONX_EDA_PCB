import networkx as nx
def connected_islands(graph):
    return [tuple(sorted(c)) for c in sorted(nx.connected_components(graph),key=lambda x:(-len(x),sorted(x)))]
