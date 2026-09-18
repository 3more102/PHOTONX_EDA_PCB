import networkx as nx
from photonx_eda_pcb.connector_paths import trace_connector_paths,validate_connector_path
from photonx_eda_pcb.connector_paths.net_sequence import path_nets
def test_connector_to_ic_path():
    g=nx.Graph();g.add_edges_from([("C:J1","N:N1"),("N:N1","C:R1"),("C:R1","N:N2"),("N:N2","C:U1")])
    p=trace_connector_paths(g,["J1"],["U1"])[0]
    assert p.hops==4 and path_nets(p)==("N1","N2")
    assert validate_connector_path(p)==[]
