def validate_protection(p):
    issues=[]
    if not 0<=p.confidence<=1:issues.append("PROTECTION_CONFIDENCE_RANGE")
    if not p.kind:issues.append("PROTECTION_KIND_EMPTY")
    return issues
