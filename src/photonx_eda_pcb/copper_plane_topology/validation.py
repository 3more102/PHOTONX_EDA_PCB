def validate_topology(topology):
    issues=[];ids={i.id for i in topology.islands}
    if len(ids)!=len(topology.islands):issues.append("PLANE_DUPLICATE_ISLAND_ID")
    for i in topology.islands:
        if i.area_mm2<=0:issues.append("PLANE_NONPOSITIVE_AREA")
    for a,neighbors in topology.adjacency.items():
        if a not in ids:issues.append("PLANE_UNKNOWN_ADJACENCY_NODE")
        for b in neighbors:
            if b not in ids:issues.append("PLANE_UNKNOWN_ADJACENCY_NODE")
    return sorted(set(issues))
