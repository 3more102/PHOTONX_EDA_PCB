def validate_dependencies(items):
    issues=[]
    for d in items:
        if d.upstream==d.downstream:issues.append("RAIL_SELF_DEPENDENCY")
        if not 0<=d.confidence<=1:issues.append("RAIL_DEPENDENCY_CONFIDENCE_RANGE")
    return issues
