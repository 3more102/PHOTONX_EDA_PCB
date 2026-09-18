VALID={"info","warning","error","critical"}
def validate_catalog(catalog):
    issues=[]
    for x in catalog.all():
        if not x.code.strip():issues.append("DIAG_EMPTY_CODE")
        if x.severity not in VALID:issues.append("DIAG_BAD_SEVERITY")
        if not x.title.strip():issues.append("DIAG_EMPTY_TITLE")
    return issues
