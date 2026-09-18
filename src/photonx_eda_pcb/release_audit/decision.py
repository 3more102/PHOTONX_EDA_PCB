def audit_passed(report):return all(c.passed for c in report.checks)
def failed_checks(report):return [c.name for c in report.checks if not c.passed]
