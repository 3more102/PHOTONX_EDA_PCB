def validate_termination(x):
    issues=[]
    if x.kind not in {"series","parallel","differential_or_series","ac"}:issues.append("TERMINATION_KIND_UNKNOWN")
    if not 0<=x.confidence<=1:issues.append("TERMINATION_CONFIDENCE_RANGE")
    if len(x.nets)!=2:issues.append("TERMINATION_NET_COUNT")
    return issues
