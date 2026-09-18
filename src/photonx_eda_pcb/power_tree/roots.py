def root_nodes(tree):
    driven={e.target for e in tree.edges if e.relation=="drives"}
    return sorted(n for n,x in tree.nodes.items() if x.kind=="source" or (x.kind=="net" and n not in driven))
