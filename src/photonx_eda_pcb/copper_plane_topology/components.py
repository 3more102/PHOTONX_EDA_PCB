def connected_components(topology):
    unseen=set(topology.adjacency);out=[]
    while unseen:
        start=min(unseen);stack=[start];comp=set()
        while stack:
            n=stack.pop()
            if n in comp:continue
            comp.add(n);unseen.discard(n)
            stack.extend(topology.adjacency.get(n,set())-comp)
        out.append(tuple(sorted(comp)))
    return sorted(out)
