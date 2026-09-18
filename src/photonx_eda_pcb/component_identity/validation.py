def validate_identity(x):
    issues=[]
    if not 0<=x.confidence<=1:issues.append("IDENTITY_CONFIDENCE_RANGE")
    if x.confidence>0 and not any((x.kind,x.value,x.footprint,x.mpn)):issues.append("IDENTITY_EMPTY")
    return issues
