def connected_components(graph):
    seen=set(); result=[]
    for node in graph.nodes():
        if node in seen: continue
        stack=[node]; component=[]
        while stack:
            current=stack.pop()
            if current in seen: continue
            seen.add(current); component.append(current); stack.extend(graph.neighbors(current))
        result.append(tuple(sorted(component)))
    return tuple(sorted(result))
