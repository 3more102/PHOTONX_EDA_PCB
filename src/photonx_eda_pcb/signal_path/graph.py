import networkx as nx
def build_signal_graph(schematic_graph):
    g=nx.Graph()
    for cid in schematic_graph.components:g.add_node("C:"+cid,kind="component",id=cid)
    for nid in schematic_graph.nets:g.add_node("N:"+nid,kind="net",id=nid)
    for cid,pin,nid in schematic_graph.pin_edges:
        g.add_edge("C:"+cid,"N:"+nid,pin=pin)
    return g
