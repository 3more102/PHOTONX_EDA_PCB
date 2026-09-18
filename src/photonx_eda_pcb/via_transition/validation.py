def validate_transition(v):
    issues=[]
    if v.drill_mm<=0:issues.append("VIA_TRANSITION_DRILL_NONPOSITIVE")
    if v.pad_mm<v.drill_mm:issues.append("VIA_TRANSITION_PAD_LT_DRILL")
    if v.stub_layers<0:issues.append("VIA_TRANSITION_NEGATIVE_STUB")
    return issues
