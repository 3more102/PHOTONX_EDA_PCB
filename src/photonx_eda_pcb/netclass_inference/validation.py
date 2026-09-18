def validate_net_classes(items):
    issues=[];seen=set()
    for x in items:
        if x.net_id in seen:issues.append("NETCLASS_DUPLICATE_NET")
        seen.add(x.net_id)
        if not 0<=x.confidence<=1:issues.append("NETCLASS_CONFIDENCE_RANGE")
    return issues
