from .metrics import semantic_metrics
def semantic_report(r):return {"metrics":semantic_metrics(r),"findings":[x.__dict__ for x in r.findings]}
