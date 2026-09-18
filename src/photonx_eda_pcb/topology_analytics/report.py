from .metrics import topology_metrics
from .hubs import high_degree_nodes
def topology_report(graph):return {"metrics":topology_metrics(graph),"hubs":high_degree_nodes(graph)}
