def impacted_objects(graph,source_id):
    start=str(source_id)
    if not start.startswith(("src:","ev:")):start="src:"+start
    seen={start};stack=[start];out=set()
    while stack:
        cur=stack.pop()
        for e in graph.edges:
            if e.source==cur and e.target not in seen:
                seen.add(e.target);stack.append(e.target)
                if graph.nodes.get(e.target) and graph.nodes[e.target].kind=="object":out.add(e.target)
    return sorted(out)
