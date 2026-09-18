def catalog_summary(c):
    fam={}
    for e in c.all():fam[e.family]=fam.get(e.family,0)+1
    return {"packages":len(c.all()),"families":dict(sorted(fam.items()))}
