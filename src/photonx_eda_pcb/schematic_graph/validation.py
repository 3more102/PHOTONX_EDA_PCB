def validate_schematic_graph(g):
    issues=[];seen=set()
    for comp,pin,net in g.pin_edges:
        if comp not in g.components:issues.append("SCHEMATIC_UNKNOWN_COMPONENT")
        if net not in g.nets:issues.append("SCHEMATIC_UNKNOWN_NET")
        key=(comp,pin)
        if key in seen:issues.append("SCHEMATIC_DUPLICATE_PIN_EDGE")
        seen.add(key)
    return issues
