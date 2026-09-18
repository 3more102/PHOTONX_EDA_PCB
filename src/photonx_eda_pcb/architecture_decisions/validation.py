VALID={"proposed","accepted","superseded","rejected"}
def validate_decision(d):
    issues=[]
    if not d.id.strip():issues.append("ADR_ID_EMPTY")
    if not d.title.strip():issues.append("ADR_TITLE_EMPTY")
    if d.status not in VALID:issues.append("ADR_STATUS_INVALID")
    if not d.decision.strip():issues.append("ADR_DECISION_EMPTY")
    return issues
