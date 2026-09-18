from .dependencies import node_dependencies
def topological_order(dag):
    deps={k:set(v) for k,v in node_dependencies(dag).items()};out=[]
    while deps:
        ready=sorted(k for k,v in deps.items() if not v)
        if not ready:raise ValueError("pipeline dependency cycle")
        for name in ready:
            out.append(name);deps.pop(name)
            for v in deps.values():v.discard(name)
    return out
