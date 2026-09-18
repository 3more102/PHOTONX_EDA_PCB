def validate_pinmap_report(r):
    issues=[]
    if r.matched<0 or r.total<0 or r.matched>r.total:issues.append("PINMAP_BAD_COUNTS")
    return issues
