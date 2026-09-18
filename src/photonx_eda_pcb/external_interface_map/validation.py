def validate_interface_map(m):
    issues=[]
    if not 0<=m.confidence<=1:issues.append("INTERFACE_MAP_CONFIDENCE_RANGE")
    return issues
