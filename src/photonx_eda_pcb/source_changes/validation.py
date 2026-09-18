VALID={"added","removed","modified"}
def validate_change_set(cs):
    issues=[];paths=set()
    for c in cs.changes:
        if c.path in paths:issues.append("CHANGESET_DUPLICATE_PATH")
        paths.add(c.path)
        if c.change_type not in VALID:issues.append("CHANGESET_BAD_TYPE")
        if c.change_type=="added" and c.after is None:issues.append("CHANGESET_ADDED_WITHOUT_AFTER")
        if c.change_type=="removed" and c.before is None:issues.append("CHANGESET_REMOVED_WITHOUT_BEFORE")
    return issues
