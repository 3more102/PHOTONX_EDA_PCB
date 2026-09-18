from .filters import component_nodes,net_nodes
def path_metrics(path):
    return {"hops":path.hops,"components":len(component_nodes(path)),"nets":len(net_nodes(path)),"confidence":path.confidence}
