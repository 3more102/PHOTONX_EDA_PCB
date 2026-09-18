def validate_records(records):
    ids=set();issues=[]
    for r in records:
        if r.id in ids:issues.append("CONNECTOR_EVIDENCE_DUPLICATE_ID")
        ids.add(r.id)
    return issues
