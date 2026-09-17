def validate_thermal(t):
    issues=[]
    if not t.pad_id:issues.append('THERMAL_PAD_MISSING')
    if not t.zone_id:issues.append('THERMAL_ZONE_MISSING')
    if t.gap_mm<0:issues.append('THERMAL_GAP_NEGATIVE')
    if len(t.spokes)<2:issues.append('THERMAL_TOO_FEW_SPOKES')
    if any(s.width_mm<=0 or s.length_mm<=0 for s in t.spokes):issues.append('THERMAL_INVALID_SPOKE')
    return issues
