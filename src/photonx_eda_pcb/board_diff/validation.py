def validate_diff(diff):
    issues=[]; seen=set()
    for e in diff.entries:
        key=(e.kind,e.object_id)
        if key in seen:issues.append('DIFF_DUPLICATE_ENTRY')
        seen.add(key)
        if e.kind not in {'added','removed','changed'}:issues.append('DIFF_KIND_UNKNOWN')
    return issues
