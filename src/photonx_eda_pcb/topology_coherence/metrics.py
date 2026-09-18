def topology_metrics(r):return {"findings":len(r.findings),"errors":sum(x.severity=="error" for x in r.findings),"warnings":sum(x.severity=="warning" for x in r.findings)}
