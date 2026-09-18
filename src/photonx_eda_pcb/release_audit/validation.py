def validate_audit(report):
    names=[c.name for c in report.checks]
    return ["AUDIT_DUPLICATE_CHECK"] if len(names)!=len(set(names)) else []
