def loads_for_net(tree,net_node):
    return sorted(e.source for e in tree.edges if e.target==net_node and e.relation=="consumes")
