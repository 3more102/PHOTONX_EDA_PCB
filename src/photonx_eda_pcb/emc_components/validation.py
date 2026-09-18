def validate_emc(x):
    issues=[]
    if x.kind not in {"ferrite","common_mode_choke"}:issues.append("EMC_KIND_UNKNOWN")
    if not 0<=x.confidence<=1:issues.append("EMC_CONFIDENCE_RANGE")
    return issues
