import networkx as nx
def articulation_components(graph):return sorted(n for n in nx.articulation_points(graph) if str(n).startswith("C:"))
def bridge_connections(graph):return sorted(tuple(sorted(e)) for e in nx.bridges(graph))
