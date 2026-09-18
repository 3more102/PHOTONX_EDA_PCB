from .score import technical_debt_score
def audit_report(a):return {"metrics":dict(a.metrics),"technical_debt_score":technical_debt_score(a),"findings":[x.__dict__ for x in a.findings]}
