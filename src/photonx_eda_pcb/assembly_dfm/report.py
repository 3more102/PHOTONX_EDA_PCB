from .score import dfm_score
def assembly_dfm_report(r):return {"score":dfm_score(r),"metrics":dict(r.metrics),"findings":[f.__dict__ for f in r.findings]}
