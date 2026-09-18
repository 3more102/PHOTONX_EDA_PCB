from .order import topological_order
def validate_dag(dag):
    issues=[]
    try:dag.producer_map()
    except ValueError:issues.append("DAG_MULTIPLE_PRODUCERS")
    try:topological_order(dag)
    except ValueError:issues.append("DAG_CYCLE")
    for n in dag.nodes.values():
        if not n.name.strip():issues.append("DAG_EMPTY_NODE_NAME")
        if set(n.requires)&set(n.produces):issues.append("DAG_SELF_ARTIFACT_DEPENDENCY")
    return issues
