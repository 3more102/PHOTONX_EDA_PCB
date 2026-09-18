def testability_report(r):return {"metrics":dict(r.metrics),"findings":[f.__dict__ for f in r.findings]}
