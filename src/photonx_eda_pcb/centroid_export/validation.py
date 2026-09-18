def validate_centroids(records):
    issues=[];seen=set()
    for r in records:
        if r.reference in seen:issues.append("CENTROID_DUPLICATE_REFERENCE")
        seen.add(r.reference)
        if r.side not in {"top","bottom","front","back","f","b"}:issues.append("CENTROID_UNKNOWN_SIDE")
    return issues
