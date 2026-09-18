def validate_power_tree(tree):
    issues=[]
    for e in tree.edges:
        if e.source not in tree.nodes or e.target not in tree.nodes:issues.append("POWER_TREE_UNKNOWN_NODE")
        if not 0<=e.confidence<=1:issues.append("POWER_TREE_CONFIDENCE_RANGE")
    return issues
