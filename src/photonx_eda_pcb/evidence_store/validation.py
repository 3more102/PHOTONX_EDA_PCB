def validate_evidence(records,known_object_ids=None):
    issues=[]; seen=set(); known=set(known_object_ids or ())
    for record in records:
        if record.id in seen: issues.append(("error","EVIDENCE_DUPLICATE_ID",record.id))
        seen.add(record.id)
        if record.object_id is not None and known and record.object_id not in known: issues.append(("warning","EVIDENCE_OBJECT_UNKNOWN",record.id,record.object_id))
        if not record.source: issues.append(("warning","EVIDENCE_SOURCE_EMPTY",record.id))
    return issues
