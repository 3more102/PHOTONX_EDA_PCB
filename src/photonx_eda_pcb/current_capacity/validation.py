def validate_capacity(x):
    issues=[]
    if min(x.width_mm,x.copper_um,x.temperature_rise_c,x.estimated_current_a)<=0:issues.append("CURRENT_CAPACITY_NONPOSITIVE")
    if not 0<=x.confidence<=1:issues.append("CURRENT_CAPACITY_CONFIDENCE_RANGE")
    return issues
