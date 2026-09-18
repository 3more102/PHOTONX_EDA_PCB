def validate_value_hypothesis(h):
    issues=[]
    if not 0<=h.confidence<=1:issues.append("VALUE_BAD_CONFIDENCE")
    if h.confidence>0 and not h.value:issues.append("VALUE_CONFIDENCE_WITHOUT_VALUE")
    return issues
