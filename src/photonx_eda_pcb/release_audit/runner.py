from .model import AuditCheck,AuditReport
def run_release_audit(*,tests_passed,unsupported_count,critical_findings,deterministic,provenance_complete):
    c=[
      AuditCheck("tests",bool(tests_passed)),
      AuditCheck("unsupported_syntax",int(unsupported_count)==0,str(unsupported_count)),
      AuditCheck("critical_findings",int(critical_findings)==0,str(critical_findings)),
      AuditCheck("determinism",bool(deterministic)),
      AuditCheck("provenance",bool(provenance_complete)),
    ]
    return AuditReport(c,{"unsupported_count":int(unsupported_count),"critical_findings":int(critical_findings)})
