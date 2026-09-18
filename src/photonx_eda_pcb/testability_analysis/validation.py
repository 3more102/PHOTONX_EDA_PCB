VALID={"info","warning","error","critical"}
def validate_testability(r):
    issues=[]
    for f in r.findings:
        if f.severity not in VALID:issues.append("TESTABILITY_BAD_SEVERITY")
    for k,v in r.metrics.items():
        if isinstance(v,float) and ("coverage" in k or "fraction" in k) and not 0<=v<=1:issues.append("TESTABILITY_METRIC_RANGE")
    return issues
