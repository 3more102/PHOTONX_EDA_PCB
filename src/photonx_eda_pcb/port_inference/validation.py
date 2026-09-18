def validate_port(p):
    issues=[]
    if not p.pins:issues.append("PORT_EMPTY_PINS")
    if not 0<=p.confidence<=1:issues.append("PORT_CONFIDENCE_RANGE")
    return issues
