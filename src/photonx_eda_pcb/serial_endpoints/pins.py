def endpoints_for_net(schematic_graph,net_id,role):
    out=[]
    for cid,pin,nid in schematic_graph.pin_edges:
        if nid==net_id:out.append((str(cid),str(pin),str(role)))
    return out
