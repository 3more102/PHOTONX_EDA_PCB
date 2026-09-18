VALID={"info","warning","error","critical"}
def validate_consistency_report(r):
    issues=[]
    for x in r.findings:
        if x.severity not in VALID:issues.append("CONSISTENCY_BAD_SEVERITY")
    return issues
