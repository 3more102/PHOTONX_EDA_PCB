def port_summary(items):
    kinds={}
    for x in items:kinds[x.kind]=kinds.get(x.kind,0)+1
    return {"ports":len(items),"kinds":dict(sorted(kinds.items()))}
