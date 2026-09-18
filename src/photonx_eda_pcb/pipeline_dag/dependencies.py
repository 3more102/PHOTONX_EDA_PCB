def node_dependencies(dag):
    producers=dag.producer_map();out={name:set() for name in dag.nodes}
    for name,node in dag.nodes.items():
        for req in node.requires:
            prod=producers.get(req)
            if prod and prod!=name:out[name].add(prod)
    return out
def reverse_dependencies(dag):
    deps=node_dependencies(dag);out={name:set() for name in deps}
    for node,parents in deps.items():
        for p in parents:out[p].add(node)
    return out
