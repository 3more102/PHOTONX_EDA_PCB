def validate_omission_manifest(data):
    issues=[]
    exported=set(data.get("exported_slots",()))
    skipped=set(data.get("skipped_slots",()))
    if exported&skipped:issues.append("OMISSION_SLOT_BOTH_EXPORTED_AND_SKIPPED")
    issue_ids={x.get("object_id") for x in data.get("issues",())}
    if not skipped.issubset(issue_ids):issues.append("OMISSION_SKIPPED_SLOT_WITHOUT_REASON")
    return issues
