def validate_traceability(m):
    issues=[];ids=set()
    for x in m.links:
        if x.claim_id in ids:issues.append("TRACE_DUPLICATE_CLAIM")
        ids.add(x.claim_id)
        if not 0<=x.confidence<=1:issues.append("TRACE_CONFIDENCE_RANGE")
        if not x.source_ids:issues.append("TRACE_SOURCE_MISSING")
    return issues
