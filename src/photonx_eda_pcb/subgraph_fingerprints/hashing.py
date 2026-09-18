import hashlib,networkx as nx
from .canonical import canonical_node_label
def topology_hash(graph):
    g=nx.Graph();g.add_nodes_from(graph.nodes);g.add_edges_from(graph.edges)
    for n in g.nodes:g.nodes[n]["label"]="C" if str(n).startswith("C:") else "N" if str(n).startswith("N:") else "X"
    return nx.weisfeiler_lehman_graph_hash(g,node_attr="label")
def semantic_hash(graph,identity_by_id=None,roles_by_net=None):
    g=nx.Graph();g.add_nodes_from(graph.nodes);g.add_edges_from(graph.edges)
    for n in g.nodes:g.nodes[n]["label"]=canonical_node_label(graph,n,identity_by_id,roles_by_net)
    raw=nx.weisfeiler_lehman_graph_hash(g,node_attr="label")
    return hashlib.sha256(raw.encode()).hexdigest()[:24]
