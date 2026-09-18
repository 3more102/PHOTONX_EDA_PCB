def role_counts(m):
    out={}
    for c in m.cases:
        for f in c.files:out[f.role]=out.get(f.role,0)+1
    return dict(sorted(out.items()))
