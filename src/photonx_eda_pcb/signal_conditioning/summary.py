def conditioning_summary(items):
    by={}
    for x in items:by[x.kind]=by.get(x.kind,0)+1
    return {"count":len(items),"kinds":dict(sorted(by.items()))}
