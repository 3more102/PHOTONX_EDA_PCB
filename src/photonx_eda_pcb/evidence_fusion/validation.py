def validate_fused(f):
    issues=[]
    if not 0<=f.confidence<=1:issues.append("FUSED_CONFIDENCE_RANGE")
    if f.confidence>0 and not f.claim:issues.append("FUSED_EMPTY_CLAIM")
    return issues
