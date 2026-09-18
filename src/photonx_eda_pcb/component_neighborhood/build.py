def build_neighborhood(component_id,schematic_graph):
    cid=str(component_id)
    nets=sorted({n for c,_,n in schematic_graph.pin_edges if c==cid})
    neighbors=set()
    for c,_,n in schematic_graph.pin_edges:
        if n in nets and c!=cid:neighbors.add(c)
    kinds=tuple(sorted(schematic_graph.components[n].kind for n in neighbors if n in schematic_graph.components))
    from .model import ComponentNeighborhood
    return ComponentNeighborhood(cid,tuple(nets),tuple(sorted(neighbors)),len(neighbors),kinds)
