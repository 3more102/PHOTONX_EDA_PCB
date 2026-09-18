def validate_si_risk(x):
    issues=[]
    if not 0<=x.score<=1:issues.append("SI_RISK_SCORE_RANGE")
    if not 0<=x.confidence<=1:issues.append("SI_RISK_CONFIDENCE_RANGE")
    if any(not 0<=v<=1 for v in x.factors.values()):issues.append("SI_RISK_FACTOR_RANGE")
    return issues
