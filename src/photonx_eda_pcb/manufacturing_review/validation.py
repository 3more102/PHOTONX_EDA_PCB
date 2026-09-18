VALID={"info","warning","error","critical"}
def validate_review(report):
    return ["REVIEW_BAD_SEVERITY" for f in report.findings if f.severity not in VALID]
