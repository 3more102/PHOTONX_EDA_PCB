def checks_report(checks):
    return {"total":len(checks),"passed":sum(c.passed is True for c in checks),"failed":sum(c.passed is False for c in checks),"unknown":sum(c.passed is None for c in checks)}
