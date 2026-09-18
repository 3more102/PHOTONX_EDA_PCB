def validation_summary(report):
    passed=sum(r.passed for r in report.results)
    return {"total":len(report.results),"passed":passed,"failed":len(report.results)-passed,"success":passed==len(report.results)}
