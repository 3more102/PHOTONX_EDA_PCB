def bundle_summary(bundle):
    roles={}
    for e in bundle.entries:roles[e.role]=roles.get(e.role,0)+1
    return {"name":bundle.name,"entries":len(bundle.entries),"roles":dict(sorted(roles.items()))}
