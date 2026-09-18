def validate_health(h):
    issues=[]
    if not 0<=h.score<=1:issues.append("HEALTH_SCORE_RANGE")
    for m in h.metrics:
        if not 0<=m.score<=1:issues.append("HEALTH_METRIC_RANGE")
        if m.weight<0:issues.append("HEALTH_NEGATIVE_WEIGHT")
    return issues
