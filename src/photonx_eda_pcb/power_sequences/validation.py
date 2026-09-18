def validate_sequence(items):
    issues=[]
    for x in items:
        if x.before==x.after:issues.append("POWER_SEQUENCE_SELF_EDGE")
        if not 0<=x.confidence<=1:issues.append("POWER_SEQUENCE_CONFIDENCE_RANGE")
    return issues
