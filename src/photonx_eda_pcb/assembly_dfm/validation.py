VALID={"info","warning","error","critical"}
def validate_report(r):
    return ["ASSEMBLY_DFM_BAD_SEVERITY" for f in r.findings if f.severity not in VALID]
