def validate_length_group(g):
    issues=[]
    if len(g.nets)<2:issues.append("LENGTH_GROUP_TOO_SMALL")
    if g.target_mm is not None and g.target_mm<0:issues.append("LENGTH_GROUP_NEGATIVE_TARGET")
    if g.tolerance_mm is not None and g.tolerance_mm<0:issues.append("LENGTH_GROUP_NEGATIVE_TOLERANCE")
    if not 0<=g.confidence<=1:issues.append("LENGTH_GROUP_CONFIDENCE_RANGE")
    return issues
