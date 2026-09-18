def consensus_for(items):
    groups={}
    for x in items:
        key=repr(x.value);g=x.independent_group or x.source
        groups.setdefault(key,{});groups[key][g]=max(groups[key].get(g,0.0),max(0.0,min(1.0,float(x.confidence))))
    scored=[]
    for value,by_group in groups.items():
        miss=1.0
        for c in by_group.values():miss*=1-c
        scored.append((1-miss,value,by_group))
    scored.sort(key=lambda x:(-x[0],x[1]))
    return scored
