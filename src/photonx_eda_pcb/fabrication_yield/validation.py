def validate_yield_risk(r):
    issues=[]
    if not 0<=r.score<=1:issues.append("YIELD_RISK_RANGE")
    if r.level not in {"low","medium","high"}:issues.append("YIELD_BAD_LEVEL")
    return issues
