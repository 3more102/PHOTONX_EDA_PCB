def validate_padstack(p):
    issues=[]
    if p.confidence<0 or p.confidence>1:issues.append("PLATED_SLOT_CONFIDENCE_RANGE")
    if len(p.layers)<2:issues.append("PLATED_SLOT_INSUFFICIENT_LAYERS")
    if min(p.pad_size)<=0 or min(p.drill_size)<=0:issues.append("PLATED_SLOT_NONPOSITIVE_SIZE")
    return issues
