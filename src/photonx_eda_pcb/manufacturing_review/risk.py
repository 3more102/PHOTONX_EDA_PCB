from .severity import severity_rank
def risk_score(report):
    return sum((severity_rank(f.severity)+1) for f in report.findings)
