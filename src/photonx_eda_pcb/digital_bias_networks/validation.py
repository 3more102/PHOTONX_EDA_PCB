def validate_bias(x):
    issues=[]
    if x.kind not in {"pull_up","pull_down"}:issues.append("BIAS_KIND_UNKNOWN")
    if not 0<=x.confidence<=1:issues.append("BIAS_CONFIDENCE_RANGE")
    return issues
