def fingerprint_differences(a,b):
    out=[]
    if a.topology_hash!=b.topology_hash:out.append("topology")
    if a.semantic_hash!=b.semantic_hash:out.append("semantics")
    if a.features.component_kinds!=b.features.component_kinds:out.append("component_kinds")
    if a.features.component_degrees!=b.features.component_degrees:out.append("component_degrees")
    if a.features.net_degrees!=b.features.net_degrees:out.append("net_degrees")
    if a.features.net_roles!=b.features.net_roles:out.append("net_roles")
    if a.features.pin_edge_count!=b.features.pin_edge_count:out.append("edge_count")
    return tuple(out)
