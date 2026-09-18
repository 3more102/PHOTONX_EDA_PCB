def validate_release_manifest(m):
    issues=[];paths=set()
    if not m.version.strip():issues.append("RELEASE_VERSION_EMPTY")
    if not m.commit.strip():issues.append("RELEASE_COMMIT_EMPTY")
    for a in m.artifacts:
        if a.path in paths:issues.append("RELEASE_DUPLICATE_PATH")
        paths.add(a.path)
        if len(a.sha256)!=64:issues.append("RELEASE_BAD_SHA256")
        if a.size<0:issues.append("RELEASE_NEGATIVE_SIZE")
    return issues
