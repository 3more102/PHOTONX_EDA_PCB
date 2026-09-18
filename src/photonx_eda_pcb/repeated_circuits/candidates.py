def exact_topology_groups(fingerprints):
    by={}
    for f in fingerprints:by.setdefault(f.topology_hash,[]).append(f)
    return [tuple(sorted(v,key=lambda x:x.seed)) for _,v in sorted(by.items()) if len(v)>=2]
