def validate_fidelity(r):
    issues=[]
    if not 0<=r.score<=1:issues.append("FIDELITY_SCORE_RANGE")
    if r.exact and any(not x.equal for x in r.sections):issues.append("FIDELITY_EXACT_CONTRADICTION")
    return issues
