def validate_dashboard(d):
    issues=[]
    if not 0<=d.overall_score<=1:issues.append("DASHBOARD_SCORE_RANGE")
    if len({c.name for c in d.cards})!=len(d.cards):issues.append("DASHBOARD_DUPLICATE_CARD")
    return issues
