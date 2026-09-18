def power_tree_metrics(tree):
    return {"nodes":len(tree.nodes),"edges":len(tree.edges),"sources":sum(n.kind=="source" for n in tree.nodes.values()),"loads":sum(n.kind=="load" for n in tree.nodes.values())}
