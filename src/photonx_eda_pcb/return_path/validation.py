def validate_return_path(e):
    issues=[]
    for name in ("continuity_score","via_penalty","confidence"):
        if not 0<=getattr(e,name)<=1:issues.append("RETURN_PATH_"+name.upper()+"_RANGE")
    if e.split_crossings<0:issues.append("RETURN_PATH_NEGATIVE_SPLITS")
    return issues
