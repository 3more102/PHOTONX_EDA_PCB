def validate_database(db):
    issues=[]
    for r in db.all():
        if not 0<=r.confidence<=1:issues.append("EVIDENCE_DB_CONFIDENCE_RANGE")
        if not r.object_id:issues.append("EVIDENCE_DB_EMPTY_OBJECT")
        if not r.kind:issues.append("EVIDENCE_DB_EMPTY_KIND")
    return issues
