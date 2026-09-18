def path_nets(path):return tuple(n[2:] for n in path.nodes if str(n).startswith("N:"))
def path_components(path):return tuple(n[2:] for n in path.nodes if str(n).startswith("C:"))
