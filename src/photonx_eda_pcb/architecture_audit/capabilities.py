def overlapping_capabilities(capability_map):
    rev={}
    for module,caps in capability_map.items():
        for cap in caps:rev.setdefault(str(cap),[]).append(str(module))
    return {k:tuple(sorted(v)) for k,v in rev.items() if len(v)>1}
