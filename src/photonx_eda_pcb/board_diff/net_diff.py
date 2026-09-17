def net_membership_diff(before,after):
    a={k:set(v) for k,v in before.items()}; b={k:set(v) for k,v in after.items()}; out={}
    for k in sorted(a.keys()|b.keys()):
        if a.get(k,set())!=b.get(k,set()):out[k]={'removed':sorted(a.get(k,set())-b.get(k,set())),'added':sorted(b.get(k,set())-a.get(k,set()))}
    return out
