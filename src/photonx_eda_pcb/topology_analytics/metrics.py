import networkx as nx
def topology_metrics(graph):
    return {"nodes":graph.number_of_nodes(),"edges":graph.number_of_edges(),"components":nx.number_connected_components(graph) if graph.number_of_nodes() else 0,"density":round(nx.density(graph),8) if graph.number_of_nodes()>1 else 0.0}
