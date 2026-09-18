def validate_peripheral_map(pmap):
    issues=[]
    for x in pmap.bindings:
        if not x.component_id:issues.append("PERIPHERAL_COMPONENT_EMPTY")
        if not x.protocol:issues.append("PERIPHERAL_PROTOCOL_EMPTY")
        if not 0<=x.confidence<=1:issues.append("PERIPHERAL_CONFIDENCE_RANGE")
        if x.role not in {"controller","peripheral"}:issues.append("PERIPHERAL_BAD_ROLE")
    return issues
