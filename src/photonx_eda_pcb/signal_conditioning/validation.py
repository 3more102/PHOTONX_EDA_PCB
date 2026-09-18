def validate_stage(x):
    issues=[]
    if not x.components:issues.append("CONDITIONING_EMPTY_COMPONENTS")
    if not 0<=x.confidence<=1:issues.append("CONDITIONING_CONFIDENCE_RANGE")
    return issues
