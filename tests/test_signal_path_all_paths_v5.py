import networkx as nx
from photonx_eda_pcb.signal_path.trace import all_paths_between
def test_all_paths_limited():
    g=nx.Graph();g.add_edges_from([("C:A","N:1"),("N:1","C:B"),("C:A","N:2"),("N:2","C:B")])
    p=all_paths_between(g,"A","B",max_paths=1)
    assert len(p)==1
