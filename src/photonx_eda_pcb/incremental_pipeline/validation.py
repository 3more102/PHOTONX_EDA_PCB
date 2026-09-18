def validate_stages(stages):
    issues=[];names=set()
    for s in stages:
        if s.name in names:issues.append("INCREMENTAL_DUPLICATE_STAGE")
        names.add(s.name)
        if s.name in s.dependencies:issues.append("INCREMENTAL_SELF_DEPENDENCY")
    return issues
