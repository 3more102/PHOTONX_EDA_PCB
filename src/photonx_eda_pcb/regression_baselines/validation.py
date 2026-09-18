def validate_baseline(b):
    issues=[]
    if not b.id.strip():issues.append("BASELINE_ID_EMPTY")
    for k,v in b.tolerances.items():
        if float(v)<0:issues.append("BASELINE_NEGATIVE_TOLERANCE")
    return issues
