def validate_records(records):
    ids=[x.id for x in records]
    issues=[]
    if len(ids)!=len(set(ids)):issues.append("SYNTH_EVIDENCE_DUPLICATE_ID")
    for x in records:
        if not 0<=x.confidence<=1:issues.append("SYNTH_EVIDENCE_CONFIDENCE_RANGE")
    return issues
