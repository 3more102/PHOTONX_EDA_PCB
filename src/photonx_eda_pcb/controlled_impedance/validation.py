def validate_constraint(c):
    issues=[]
    if c.target_ohms<=0:issues.append("IMPEDANCE_TARGET_NONPOSITIVE")
    if c.tolerance_ohms<0:issues.append("IMPEDANCE_TOLERANCE_NEGATIVE")
    if c.mode not in {"single-ended","differential"}:issues.append("IMPEDANCE_MODE_UNKNOWN")
    return issues
