import networkx as nx
from photonx_eda_pcb.topology_analytics.critical import articulation_components,bridge_connections
def test_critical_nodes():
    g=nx.Graph();g.add_edges_from([("N:1","C:R1"),("C:R1","N:2")])
    assert articulation_components(g)==["C:R1"]
    assert len(bridge_connections(g))==2
