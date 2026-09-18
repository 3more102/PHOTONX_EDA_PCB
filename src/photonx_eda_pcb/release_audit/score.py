def audit_score(report):
    return 1.0 if not report.checks else round(sum(c.passed for c in report.checks)/len(report.checks),6)
