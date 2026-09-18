import networkx as nx
from photonx_eda_pcb.graph_layout import layout_components,validate_layout
from photonx_eda_pcb.graph_layout.normalize import normalize_layout
def test_graph_layout_deterministic_and_unique():
    g=nx.Graph();g.add_edges_from([("C:A","N:1"),("N:1","C:B"),("C:B","N:2"),("N:2","C:C")])
    a=normalize_layout(layout_components(g));b=normalize_layout(layout_components(g))
    assert a.positions==b.positions and validate_layout(a)==[]
