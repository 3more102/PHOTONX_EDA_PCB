def validate_guess(g):
    issues=[]
    if not 0<=g.confidence<=1:issues.append("FORMAT_CONFIDENCE_RANGE")
    if not g.format:issues.append("FORMAT_EMPTY")
    return issues
