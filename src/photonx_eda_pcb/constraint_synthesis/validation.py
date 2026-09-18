def validate_constraint_set(s):
    issues=[];seen=set()
    for c in s.constraints:
        if c.net_id in seen:issues.append("CONSTRAINT_DUPLICATE_NET")
        seen.add(c.net_id)
        if not 0<=c.confidence<=1:issues.append("CONSTRAINT_CONFIDENCE_RANGE")
        for v in (c.min_width_mm,c.clearance_mm,c.target_length_mm,c.length_tolerance_mm,c.diff_pair_gap_mm):
            if v is not None and v<0:issues.append("CONSTRAINT_NEGATIVE_VALUE")
    return issues
