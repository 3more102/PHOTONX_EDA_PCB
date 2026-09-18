def validate_group(g):
    issues=[]
    if not 0<=g.quality_score<=1:issues.append("DECOUPLING_GROUP_QUALITY_RANGE")
    if not 0<=g.confidence<=1:issues.append("DECOUPLING_GROUP_CONFIDENCE_RANGE")
    return issues
