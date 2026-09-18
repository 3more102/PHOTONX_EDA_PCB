import networkx as nx
def build_net_component_graph(schematic_graph):
    g=nx.Graph()
    for cid in schematic_graph.components:g.add_node("C:"+cid,kind="component")
    for nid in schematic_graph.nets:g.add_node("N:"+nid,kind="net")
    for cid,pin,nid in schematic_graph.pin_edges:g.add_edge("C:"+cid,"N:"+nid,pin=pin)
    return g
