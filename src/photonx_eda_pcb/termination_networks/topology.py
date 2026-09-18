def component_nets(schematic_graph,component_id):
    return tuple(sorted({nid for cid,_,nid in schematic_graph.pin_edges if cid==str(component_id)}))
def components_on_net(schematic_graph,net_id):
    return tuple(sorted({cid for cid,_,nid in schematic_graph.pin_edges if nid==str(net_id)}))
