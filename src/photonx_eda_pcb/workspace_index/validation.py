def validate_index(index):
    issues=[];seen=set()
    for a in index.artifacts:
        if a.path in seen:issues.append("WORKSPACE_DUPLICATE_PATH")
        seen.add(a.path)
        if a.size<0:issues.append("WORKSPACE_NEGATIVE_SIZE")
        if a.sha256 and len(a.sha256)!=64:issues.append("WORKSPACE_BAD_SHA256")
    return issues
