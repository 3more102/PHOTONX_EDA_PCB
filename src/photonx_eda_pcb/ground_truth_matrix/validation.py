def validate_case(c):
    issues=[]
    if not c.id:issues.append("GROUND_TRUTH_ID_EMPTY")
    for k,v in c.tolerances.items():
        if float(v)<0:issues.append("GROUND_TRUTH_NEGATIVE_TOLERANCE")
    return issues
