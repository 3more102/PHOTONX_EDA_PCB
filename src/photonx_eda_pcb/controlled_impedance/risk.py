def risk_level(check):
    if check.passed is None:return "unknown"
    if check.passed:return "low"
    if check.error_ohms is not None and check.error_ohms>30:return "high"
    return "medium"
