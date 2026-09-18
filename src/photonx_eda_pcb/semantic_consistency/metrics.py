def semantic_metrics(r):
    sev={}
    for x in r.findings:sev[x.severity]=sev.get(x.severity,0)+1
    return {"findings":len(r.findings),"severity":dict(sorted(sev.items()))}
