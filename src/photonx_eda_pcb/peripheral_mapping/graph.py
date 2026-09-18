def components_on_nets(schematic_graph,nets):
    want=set(map(str,nets));out=set()
    for cid,_,nid in schematic_graph.pin_edges:
        if nid in want:out.add(str(cid))
    return sorted(out)
def pins_on_nets(schematic_graph,component_id,nets):
    want=set(map(str,nets))
    return tuple(sorted((str(pin),str(nid)) for cid,pin,nid in schematic_graph.pin_edges if cid==str(component_id) and nid in want))
