import networkx as nx
def betweenness(graph):
    return {k:round(v,8) for k,v in sorted(nx.betweenness_centrality(graph).items())}
