def validate_generated_netclass(c):
    issues=[]
    if not c.nets:issues.append("NETCLASS_EMPTY_NETS")
    if c.min_width_mm<0 or c.clearance_mm<0:issues.append("NETCLASS_NEGATIVE_RULE")
    if not 0<=c.confidence<=1:issues.append("NETCLASS_CONFIDENCE_RANGE")
    return issues
