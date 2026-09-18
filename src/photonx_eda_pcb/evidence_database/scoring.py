def object_confidence(records):
    groups={}
    for r in records:
        g=r.group or r.source or r.id;groups[g]=max(groups.get(g,0.0),float(r.confidence))
    miss=1.0
    for c in groups.values():miss*=1-max(0,min(1,c))
    return round(1-miss,12)
