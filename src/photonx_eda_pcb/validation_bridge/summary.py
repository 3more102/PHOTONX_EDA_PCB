def unified_summary(items):
    sev={};src={}
    for x in items:
        sev[x.severity]=sev.get(x.severity,0)+1
        src[x.source]=src.get(x.source,0)+1
    return {"total":len(items),"severity":dict(sorted(sev.items())),"sources":dict(sorted(src.items()))}
