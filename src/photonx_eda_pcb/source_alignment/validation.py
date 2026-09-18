def validate_alignment(transform):
    issues=[]
    if transform.scale<=0:issues.append("ALIGN_SCALE_NONPOSITIVE")
    if abs(transform.rotation_deg)>3600:issues.append("ALIGN_ROTATION_EXTREME")
    return issues
