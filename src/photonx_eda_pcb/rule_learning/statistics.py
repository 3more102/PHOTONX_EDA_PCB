def percentile(values,p):
    xs=sorted(float(x) for x in values)
    if not xs:return None
    if len(xs)==1:return xs[0]
    pos=(len(xs)-1)*float(p);lo=int(pos);hi=min(lo+1,len(xs)-1);frac=pos-lo
    return xs[lo]*(1-frac)+xs[hi]*frac
