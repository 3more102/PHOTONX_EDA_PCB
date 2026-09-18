def compare_learned(a,b):
    keys=sorted(set(a.rules)|set(b.rules));out={}
    for k in keys:
        av=a.rules.get(k);bv=b.rules.get(k)
        out[k]=(None if av is None else av.value,None if bv is None else bv.value)
    return out
