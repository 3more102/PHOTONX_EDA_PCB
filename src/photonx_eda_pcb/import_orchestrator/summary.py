def import_summary(results):
    ok=sum(r.success for r in results)
    by={}
    for r in results:by[r.format]=by.get(r.format,0)+1
    return {"total":len(results),"passed":ok,"failed":len(results)-ok,"formats":dict(sorted(by.items()))}
