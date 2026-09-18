def validate_pattern(p):
    issues=[]
    if not p.name.strip():issues.append("PATTERN_NAME_EMPTY")
    if p.min_components<0:issues.append("PATTERN_MIN_NEGATIVE")
    if p.max_components is not None and p.max_components<p.min_components:issues.append("PATTERN_MAX_LT_MIN")
    return issues
