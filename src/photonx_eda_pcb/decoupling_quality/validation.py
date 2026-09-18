def validate_decoupling_quality(x):
    issues=[]
    if not 0<=x.score<=1:issues.append("DECOUPLING_SCORE_RANGE")
    if not 0<=x.confidence<=1:issues.append("DECOUPLING_CONFIDENCE_RANGE")
    return issues
