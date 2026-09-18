def overlapping_components(domains):
    seen={};out={}
    for d in domains:
        for c in d.components:seen.setdefault(c,[]).append(d.name)
    for c,names in seen.items():
        if len(names)>1:out[c]=tuple(sorted(names))
    return out
