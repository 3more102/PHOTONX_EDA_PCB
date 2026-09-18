def diff_stats(a,b):
    out={}
    for k in a.__dataclass_fields__:
        av=getattr(a,k);bv=getattr(b,k)
        if av!=bv:out[k]=(av,bv)
    return out
