def validate_bridge_records(records):
    issues=[];ids=set()
    for r in records:
        if r.id in ids:issues.append("ENGINEERING_EVIDENCE_DUPLICATE_ID")
        ids.add(r.id)
        if not 0<=r.confidence<=1:issues.append("ENGINEERING_EVIDENCE_CONFIDENCE_RANGE")
    return issues
