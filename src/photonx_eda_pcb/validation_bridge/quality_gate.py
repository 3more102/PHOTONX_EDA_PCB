def counts_for_quality_gate(items):
    out={}
    for x in items:out[x.severity]=out.get(x.severity,0)+1
    return out
