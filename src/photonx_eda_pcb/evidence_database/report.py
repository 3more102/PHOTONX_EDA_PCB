def database_summary(db):
    kinds={}
    for r in db.all():kinds[r.kind]=kinds.get(r.kind,0)+1
    return {"records":len(db),"kinds":dict(sorted(kinds.items()))}
