def validate_thermal_risk(r):
    issues=[]
    if not 0<=r.risk<=1:issues.append("THERMAL_RISK_RANGE")
    if not 0<=r.confidence<=1:issues.append("THERMAL_CONFIDENCE_RANGE")
    return issues
