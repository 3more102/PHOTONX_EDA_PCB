def fidelity_status(report):
    if report.exact:return "exact"
    if report.score>=.95:return "high"
    if report.score>=.8:return "partial"
    return "poor"
