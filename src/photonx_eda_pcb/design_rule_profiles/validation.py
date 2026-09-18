def validate_profile(p):
    issues=[]
    for name in ("min_track_mm","min_clearance_mm","min_drill_mm","min_annular_mm","min_mask_sliver_mm"):
        if float(getattr(p,name))<0:issues.append("RULE_NEGATIVE_"+name.upper())
    return issues
