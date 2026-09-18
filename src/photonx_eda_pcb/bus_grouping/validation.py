def validate_bus(b):
    issues=[]
    if b.width!=len(b.net_ids) or b.width!=len(b.indices):issues.append("BUS_WIDTH_MISMATCH")
    if len(set(b.net_ids))!=len(b.net_ids):issues.append("BUS_DUPLICATE_NET")
    if len(set(b.indices))!=len(b.indices):issues.append("BUS_DUPLICATE_INDEX")
    if not 0<=b.confidence<=1:issues.append("BUS_CONFIDENCE_RANGE")
    return issues
