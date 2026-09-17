def validate_manifest(manifest):
    issues=[]; seen=set()
    if not manifest.name.strip(): issues.append(("error","MANIFEST_NAME_EMPTY"))
    for source in manifest.sources:
        if source.path in seen: issues.append(("warning","MANIFEST_DUPLICATE_SOURCE",source.path))
        seen.add(source.path)
        if not source.role: issues.append(("warning","MANIFEST_ROLE_EMPTY",source.path))
    return issues
