from .metrics import topology_metrics
def topology_report(r):return {"metrics":topology_metrics(r),"findings":[x.__dict__ for x in r.findings]}
