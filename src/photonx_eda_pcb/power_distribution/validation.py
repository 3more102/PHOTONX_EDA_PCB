def validate_power_evidence(x):
    issues=[]
    if not 0<=x.confidence<=1:issues.append("PDN_CONFIDENCE_RANGE")
    if x.estimated_resistance_ohm is not None and x.estimated_resistance_ohm<0:issues.append("PDN_NEGATIVE_RESISTANCE")
    return issues
