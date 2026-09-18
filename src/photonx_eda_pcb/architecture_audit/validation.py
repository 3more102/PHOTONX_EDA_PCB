VALID={"info","warning","error","critical"}
def validate_audit(a):
    return ["ARCH_AUDIT_BAD_SEVERITY" for x in a.findings if x.severity not in VALID]
