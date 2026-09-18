def validate_hierarchy(result):
    issues=[];seen=set()
    for b in result.blocks:
        if b.id in seen:issues.append("HIERARCHY_DUPLICATE_BLOCK")
        seen.add(b.id)
        if not 0<=b.confidence<=1:issues.append("HIERARCHY_CONFIDENCE_RANGE")
        if len(b.component_ids)!=len(set(b.component_ids)):issues.append("HIERARCHY_DUPLICATE_COMPONENT")
    return issues
