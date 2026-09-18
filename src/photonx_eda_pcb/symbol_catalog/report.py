def catalog_summary(c):
    kinds={}
    for e in c.all():kinds[e.kind]=kinds.get(e.kind,0)+1
    return {"symbols":len(c.all()),"kinds":dict(sorted(kinds.items()))}
