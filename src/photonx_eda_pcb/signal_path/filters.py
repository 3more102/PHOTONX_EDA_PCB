def component_nodes(path):return tuple(n for n in path.nodes if n.startswith("C:"))
def net_nodes(path):return tuple(n for n in path.nodes if n.startswith("N:"))
