def validate_candidates(items):
    issues=[]
    for x in items:
        if not 0<=x.confidence<=1:issues.append("PROTOCOL_CONFIDENCE_RANGE")
        if len(x.net_ids)!=len(set(x.net_ids)):issues.append("PROTOCOL_DUPLICATE_NET")
    return issues
