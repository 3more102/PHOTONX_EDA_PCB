def validate_risk(r):
    issues=[]
    if not 0<=r.score<=1:issues.append("MFG_RISK_SCORE_RANGE")
    if any(not 0<=x.score<=1 for x in r.items):issues.append("MFG_RISK_ITEM_RANGE")
    return issues
