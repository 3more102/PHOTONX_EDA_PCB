VALID_ACTION={"add","remove","modify","added","removed","modified"}
def validate_eco(eco):
    issues=[];ids=set()
    for x in eco.changes:
        if x.id in ids:issues.append("ECO_DUPLICATE_ID")
        ids.add(x.id)
        if x.action not in VALID_ACTION:issues.append("ECO_BAD_ACTION")
    return issues
