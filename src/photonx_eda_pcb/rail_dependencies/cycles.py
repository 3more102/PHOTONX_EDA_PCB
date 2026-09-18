import networkx as nx
def dependency_cycles(dependencies):
    from .graph import dependency_graph
    return [tuple(x) for x in nx.simple_cycles(dependency_graph(dependencies))]
