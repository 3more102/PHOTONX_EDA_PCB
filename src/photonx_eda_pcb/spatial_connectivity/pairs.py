def candidate_pairs(index,tolerance=0.0):
    out=set()
    for oid in index.ids():
        q=index.query(index.box(oid).expanded(tolerance))
        for other in q:
            if other==oid:continue
            out.add(tuple(sorted((oid,other))))
    return sorted(out)
