def validate_resolved_name(x):
    issues=[]
    if not 0<=x.confidence<=1:issues.append("NET_NAME_CONFIDENCE_RANGE")
    if x.confidence>0 and not x.name:issues.append("NET_NAME_CONFIDENCE_WITHOUT_NAME")
    return issues
