def compare_release_manifests(a,b):
    xa={x.path:x for x in a.artifacts};xb={x.path:x for x in b.artifacts};out=[]
    for p in sorted(set(xa)|set(xb)):
        if p not in xa:out.append((p,"added"))
        elif p not in xb:out.append((p,"removed"))
        elif xa[p].sha256!=xb[p].sha256:out.append((p,"modified"))
    return out
