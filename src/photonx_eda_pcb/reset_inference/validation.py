def validate_reset(r):
    issues=[]
    if not 0<=r.confidence<=1:issues.append("RESET_CONFIDENCE_RANGE")
    if r.fanout<0:issues.append("RESET_NEGATIVE_FANOUT")
    return issues
