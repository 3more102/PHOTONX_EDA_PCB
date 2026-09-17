def validate_candidate(c):
    issues=[]
    if not c.object_ids:issues.append(('error','REPAIR_NO_OBJECTS'))
    if not 0<=c.confidence<=1:issues.append(('error','REPAIR_CONFIDENCE_INVALID'))
    if c.automatic and c.kind in {'bridge_gap','review_self_touch'}:issues.append(('error','UNSAFE_AUTOMATIC_REPAIR'))
    return issues
