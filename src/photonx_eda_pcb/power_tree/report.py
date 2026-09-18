def power_tree_report(tree):
    return {"nodes":[{"id":n.id,"kind":n.kind,"voltage":n.voltage} for n in sorted(tree.nodes.values(),key=lambda x:x.id)],"edges":[{"source":e.source,"target":e.target,"relation":e.relation,"confidence":e.confidence} for e in tree.edges]}
