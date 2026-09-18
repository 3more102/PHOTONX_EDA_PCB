from .severity import severity_rank
def release_decision(report,max_allowed="warning"):
    limit=severity_rank(max_allowed)
    blockers=[f for f in report.findings if severity_rank(f.severity)>limit]
    return {"ready":not blockers,"blockers":[f.code for f in blockers]}
