VALID_SEVERITY={"info","warning","error","critical"}
def validate_registry(registry):
    issues=[]
    for check,_ in registry.items():
        if check.severity not in VALID_SEVERITY:issues.append("VALIDATION_BAD_SEVERITY")
        if not check.name.strip():issues.append("VALIDATION_EMPTY_NAME")
    return issues
