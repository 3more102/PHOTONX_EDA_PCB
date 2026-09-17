import networkx as nx

def build_connectivity_graph(board):
    g=nx.Graph()
    for n in board.nets:
        nnode='net:'+n.id; g.add_node(nnode,kind='net',confidence=n.confidence,label=n.label)
        for m in n.members:g.add_node(m,kind='object'); g.add_edge(nnode,m)
    for c in board.components:
        cnode='component:'+c.id; g.add_node(cnode,kind='component',confidence=c.confidence)
        for p in c.pad_ids:g.add_node(p,kind='object'); g.add_edge(cnode,p)
    return g
