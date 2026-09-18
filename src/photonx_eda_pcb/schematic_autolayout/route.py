from photonx_eda_pcb.wire_routing import route_manhattan,count_crossings
def route_page_nets(graph,positions,net_ids):
    routes=[]
    for net in sorted(map(str,net_ids)):
        node="N:"+net
        if node not in graph:continue
        comps=sorted(n[2:] for n in graph.neighbors(node) if str(n).startswith("C:") and n[2:] in positions)
        if len(comps)<2:continue
        anchor=comps[0]
        for other in comps[1:]:
            a=positions[anchor];b=positions[other]
            routes.append(route_manhattan(net,(a.x,a.y),(b.x,b.y),True))
    return routes,count_crossings(routes)
