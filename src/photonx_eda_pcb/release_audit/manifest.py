def audit_manifest(report):
    return {"checks":[{"name":c.name,"passed":c.passed,"details":c.details} for c in report.checks],"metadata":dict(report.metadata)}
