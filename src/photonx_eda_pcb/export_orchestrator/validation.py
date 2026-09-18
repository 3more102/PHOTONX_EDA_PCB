def validate_export_requests(requests):
    issues=[];seen=set()
    for r in requests:
        if r.id in seen:issues.append("EXPORT_DUPLICATE_ID")
        seen.add(r.id)
        if not r.format.strip():issues.append("EXPORT_EMPTY_FORMAT")
    return issues
